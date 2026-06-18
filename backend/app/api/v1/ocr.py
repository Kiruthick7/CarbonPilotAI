from typing import Any

import structlog
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel

from app.dependencies import get_calculator
from app.services.calculator_service import CalculatorService
from app.services.inventory_builder import build_inventory_for_data
from app.services.ocr_service import process_document

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/ocr", tags=["ocr"])

class ManualEntryRequest(BaseModel):
    kwh_usage: float

class IndividualResult(BaseModel):
    filename: str
    kwh_usage: float
    total_cost_usd: float | None
    confidence: float
    calculated_footprint_tco2e: float
    profile: dict[str, Any]
    inventory: dict[str, Any]

class OcrResponse(BaseModel):
    success: bool
    filename: str
    kwh_usage: float
    total_cost_usd: float | None
    confidence: float
    calculated_footprint_tco2e: float
    profile: dict[str, Any]
    inventory: dict[str, Any]
    individual_results: list[IndividualResult]


@router.post("/upload", response_model=OcrResponse)
async def upload_utility_bill(
    files: list[UploadFile] = File(...),
    calculator: CalculatorService = Depends(get_calculator)
) -> OcrResponse:
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
        aggregated_parsed: dict[str, float] = {}
        processed_filenames: list[str] = []
        individual_results: list[IndividualResult] = []

        for file in files:
            if file.content_type not in ALLOWED_TYPES:
                raise HTTPException(status_code=415, detail=f"Unsupported file: {file.filename}")

            file_bytes = await file.read()
            if len(file_bytes) > 5 * 1024 * 1024:
                raise HTTPException(status_code=413, detail=f"File exceeds 5MB limit: {file.filename}")


            ocr_result = process_document(file_bytes, file.filename or "unknown")
            if "error" in ocr_result:
                raise HTTPException(status_code=400, detail=str(ocr_result["error"]))

            if float(ocr_result.get("confidence", 1.0)) < 0.3:
                raise HTTPException(status_code=422, detail="OCR confidence too low. Please use manual entry.")

            processed_filenames.append(file.filename or "unknown")
            file_kwh = float(ocr_result.get("kwh_usage") or 0.0)
            file_cost = float(ocr_result.get("total_cost") or 0.0)
            file_conf = float(ocr_result.get("confidence", 0.0))

            total_kwh += file_kwh
            total_cost += file_cost
            total_confidence += file_conf

            parsed_for_file = ocr_result.get("parsed_footprints")
            if isinstance(parsed_for_file, dict):
                for cat, val in parsed_for_file.items():
                    if isinstance(val, (int, float)):
                        if cat in aggregated_parsed:
                            aggregated_parsed[cat] += float(val)
                        else:
                            aggregated_parsed[cat] = float(val)

            ind_profile, ind_inventory, ind_calc_footprint = await build_inventory_for_data(
                calculator, file_kwh, aggregated_parsed
            )
            individual_results.append(IndividualResult(
                filename=file.filename or "unknown",
                kwh_usage=file_kwh,
                total_cost_usd=file_cost if file_cost > 0 else None,
                confidence=file_conf,
                calculated_footprint_tco2e=ind_calc_footprint,
                profile=ind_profile.model_dump(),
                inventory=ind_inventory.model_dump()
            ))

        avg_confidence = total_confidence / len(files) if files else 0.0
        combined_filename = ", ".join(processed_filenames)

        combined_profile, combined_inventory, footprint_tco2e = await build_inventory_for_data(
            calculator, total_kwh, aggregated_parsed
        )

        response_data = OcrResponse(
            success=True,
            filename=combined_filename,
            kwh_usage=total_kwh,
            total_cost_usd=total_cost if total_cost > 0 else None,
            confidence=avg_confidence,
            calculated_footprint_tco2e=footprint_tco2e,
            profile=combined_profile.model_dump(),
            inventory=combined_inventory.model_dump(),
            individual_results=individual_results
        )

        logger.info("ocr_upload_completed", result={"success": True, "file_count": len(files), "total_kwh": total_kwh})
        return response_data

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("ocr_upload_failed", error=str(e))
        raise

@router.post("/manual", response_model=OcrResponse)
async def manual_utility_entry(
    request: ManualEntryRequest,
    calculator: CalculatorService = Depends(get_calculator)
) -> OcrResponse:
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

        individual_results = [IndividualResult(
            filename="Manual Entry",
            kwh_usage=total_kwh,
            total_cost_usd=None,
            confidence=1.0,
            calculated_footprint_tco2e=ind_calc_footprint,
            profile=ind_profile.model_dump(),
            inventory=ind_inventory.model_dump()
        )]

        response_data = OcrResponse(
            success=True,
            filename="Manual Entry",
            kwh_usage=total_kwh,
            total_cost_usd=None,
            confidence=1.0,
            calculated_footprint_tco2e=ind_calc_footprint,
            profile=ind_profile.model_dump(),
            inventory=ind_inventory.model_dump(),
            individual_results=individual_results
        )

        logger.info("manual_entry_completed", result={"success": True, "total_kwh": total_kwh})
        return response_data

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("manual_entry_failed", error=str(e))
        raise
