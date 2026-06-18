import { z } from "zod";

export const CarbonInventorySchema = z
  .object({
    total_tco2e: z.number().optional(),
    breakdowns: z
      .array(
        z.object({
          category: z.string(),
          total_kgco2e: z.number(),
        }),
      )
      .optional(),
    trace: z.record(z.string(), z.unknown()).optional(),
  })
  .passthrough();

export const CarbonProfileSchema = z
  .object({
    digital: z
      .object({
        device_upgrade_frequency: z.string().nullable().optional(),
        streaming_gaming_usage: z.string().nullable().optional(),
        ai_cloud_usage: z.string().nullable().optional(),
      })
      .nullable()
      .optional(),
  })
  .passthrough();

export const OcrDataSchema: z.ZodType<unknown> = z.lazy(() =>
  z
    .object({
      success: z.boolean().optional(),
      filename: z.string().optional(),
      kwh_usage: z.number().optional(),
      total_cost_usd: z.number().nullable().optional(),
      confidence: z.number().optional(),
      calculated_footprint_tco2e: z.number().optional(),
      inventory: CarbonInventorySchema,
      profile: CarbonProfileSchema,
      individual_results: z
        .array(
          z.lazy(() => OcrDataSchema.and(z.object({ filename: z.string() }))),
        )
        .optional(),
    })
    .passthrough(),
);

export type ZodOcrData = z.infer<typeof OcrDataSchema>;
