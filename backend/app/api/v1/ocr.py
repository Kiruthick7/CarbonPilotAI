import structlog
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel

from app.dependencies import get_calculator
from app.models.carbon import (
    CarbonProfile,
    HeatingType,
    HomeProfile,
    HomeSize,
)
from app.services.calculator_service import CalculatorService
from app.services.ocr_service import process_document

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/ocr", tags=["ocr"])

class ManualEntryRequest(BaseModel):
    kwh_usage: float

async def build_inventory_for_data(calculator: CalculatorService, kwh: float, parsed: dict):

    profile = CarbonProfile(
        country_code="US",
        transport=None,
        diet=None,
        home=HomeProfile(home_size=HomeSize.MEDIUM, heating_type=HeatingType.GAS, num_occupants=2, has_solar=False, renewable_tariff=False),
        consumption=None
    )


    calc_result = await calculator.calculate(profile)
    inventory = calc_result["inventory"]

    footprint_kg = kwh * 0.385
    footprint_tco2e = round(footprint_kg / 1000.0, 3)


    new_total_tco2e = 0.0

    existing_cats = set()
    for breakdown in inventory.breakdowns:
        cat = breakdown.category
        existing_cats.add(cat)

        if cat in parsed:
            val_tco2e = parsed[cat]
            val_kg = val_tco2e * 1000.0

            breakdown.total_kgco2e = val_kg
            if cat == "home":
                for sub in breakdown.subcategories:
                    if sub.label.lower() == "electricity":
                        sub.kgco2e = val_kg
                        sub.share_of_category = 1.0
                    else:
                        sub.kgco2e = 0.0
                        sub.share_of_category = 0.0
            else:
                if breakdown.subcategories:
                    breakdown.subcategories[0].kgco2e = val_kg
                    breakdown.subcategories[0].share_of_category = 1.0
                    for sub in breakdown.subcategories[1:]:
                        sub.kgco2e = 0.0
                        sub.share_of_category = 0.0

            new_total_tco2e += val_tco2e

        elif cat == "home" and "home" not in parsed and kwh > 0:
            breakdown.total_kgco2e = footprint_kg
            for sub in breakdown.subcategories:
                if sub.label.lower() == "electricity":
                    sub.kgco2e = footprint_kg
                    sub.share_of_category = 1.0
                else:
                    sub.kgco2e = 0.0
                    sub.share_of_category = 0.0
            new_total_tco2e += footprint_tco2e

    from app.models.carbon import CategoryBreakdown, SubcategoryItem
    for parsed_cat, parsed_tco2e in parsed.items():
        if parsed_cat not in existing_cats:
            val_kg = parsed_tco2e * 1000.0
            new_breakdown = CategoryBreakdown(
                category=parsed_cat,
                total_kgco2e=val_kg,
                subcategories=[SubcategoryItem(label="Extracted from Bill", kgco2e=val_kg, share_of_category=1.0)]
            )
            inventory.breakdowns.append(new_breakdown)
            new_total_tco2e += parsed_tco2e

    inventory.total_tco2e = round(new_total_tco2e, 3)
    return profile, inventory, footprint_tco2e

@router.post("/upload")
async def upload_utility_bill(
    files: list[UploadFile] = File(...),
    calculator: CalculatorService = Depends(get_calculator)
):
    """
    Process an uploaded utility bill image or PDF.
    Generates a full baseline CarbonProfile and CarbonInventory, injecting the OCR footprint.
    """
    logger.info("ocr_upload_started", file_count=len(files))

    try:
        ALLOWED_TYPES = ["application/pdf", "image/png", "image/jpeg", "image/jpg"]

        total_kwh = 0.0
        total_cost = 0.0
        total_confidence = 0.0
        aggregated_parsed = {}
        processed_filenames = []
        individual_results = []

        for file in files:
            if file.content_type not in ALLOWED_TYPES:
                raise HTTPException(status_code=415, detail=f"Unsupported file: {file.filename}")

            file_bytes = await file.read()
            if len(file_bytes) > 5 * 1024 * 1024:
                raise HTTPException(status_code=413, detail=f"File exceeds 5MB limit: {file.filename}")


            ocr_result = process_document(file_bytes, file.filename or "unknown")
            if "error" in ocr_result:
                raise HTTPException(status_code=400, detail=ocr_result["error"])

            if ocr_result.get("confidence", 1.0) < 0.3:
                raise HTTPException(status_code=422, detail="OCR confidence too low. Please use manual entry.")

            processed_filenames.append(file.filename or "unknown")
            file_kwh = ocr_result.get("kwh_usage") or 0.0
            file_cost = ocr_result.get("total_cost") or 0.0
            file_conf = ocr_result.get("confidence", 0.0)

            total_kwh += file_kwh
            total_cost += file_cost
            total_confidence += file_conf


            parsed_for_file = ocr_result.get("parsed_footprints", {})
            for cat, val in parsed_for_file.items():
                if cat in aggregated_parsed:
                    aggregated_parsed[cat] += val
                else:
                    aggregated_parsed[cat] = val


            ind_profile, ind_inventory, ind_calc_footprint = await build_inventory_for_data(
                calculator, file_kwh, parsed_for_file
            )
            individual_results.append({
                "filename": file.filename,
                "kwh_usage": file_kwh,
                "total_cost_usd": file_cost if file_cost > 0 else None,
                "confidence": file_conf,
                "calculated_footprint_tco2e": ind_calc_footprint,
                "profile": ind_profile.model_dump(),
                "inventory": ind_inventory.model_dump()
            })

        avg_confidence = total_confidence / len(files) if files else 0.0
        combined_filename = ", ".join(processed_filenames)


        combined_profile, combined_inventory, footprint_tco2e = await build_inventory_for_data(
            calculator, total_kwh, aggregated_parsed
        )


        response_data = {
            "success": True,
            "filename": combined_filename,
            "kwh_usage": total_kwh,
            "total_cost_usd": total_cost if total_cost > 0 else None,
            "confidence": avg_confidence,
            "calculated_footprint_tco2e": footprint_tco2e,
            "profile": combined_profile.model_dump(),
            "inventory": combined_inventory.model_dump(),
            "individual_results": individual_results
        }

        logger.info("ocr_upload_completed", result={"success": True, "file_count": len(files), "total_kwh": total_kwh})
        return response_data

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("ocr_upload_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to process document locally.")

@router.post("/manual")
async def manual_utility_entry(
    request: ManualEntryRequest,
    calculator: CalculatorService = Depends(get_calculator)
):
    """
    Process manual utility data.
    Generates a full baseline CarbonProfile and CarbonInventory, bypassing OCR.
    """
    logger.info("manual_entry_started", kwh=request.kwh_usage)

    try:
        total_kwh = request.kwh_usage


        ind_profile, ind_inventory, ind_calc_footprint = await build_inventory_for_data(
            calculator, total_kwh, {}
        )

        individual_results = [{
            "filename": "Manual Entry",
            "kwh_usage": total_kwh,
            "total_cost_usd": None,
            "confidence": 1.0,
            "calculated_footprint_tco2e": ind_calc_footprint,
            "profile": ind_profile.model_dump(),
            "inventory": ind_inventory.model_dump()
        }]

        response_data = {
            "success": True,
            "filename": "Manual Entry",
            "kwh_usage": total_kwh,
            "total_cost_usd": None,
            "confidence": 1.0,
            "calculated_footprint_tco2e": ind_calc_footprint,
            "profile": ind_profile.model_dump(),
            "inventory": ind_inventory.model_dump(),
            "individual_results": individual_results
        }

        logger.info("manual_entry_completed", result={"success": True, "total_kwh": total_kwh})
        return response_data

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("manual_entry_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to process manual entry.")
