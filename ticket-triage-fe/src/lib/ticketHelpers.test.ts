import { describe, expect, it } from "vitest";
import { AspectMetaItem, AspectStatItem } from "../api/schema";
import {
  ALLOWED_STATUS_TRANSITIONS,
  buildAspectSentimentMatrix,
  canTransitionStatus,
  CRITICAL_EVIDENCE_TERMS,
  findEvidenceRanges,
  getAspectDisplayName,
  getEvidenceLevel,
  getEvidenceTone,
  HIGH_EVIDENCE_TERMS,
  resolvePriorityLevel,
} from "./ticketHelpers";

const SAMPLE_META: AspectMetaItem[] = [
  {
    id: "refund_payment",
    name_vi: "Hoàn tiền & Thanh toán",
    description: "Khiếu nại hoàn tiền",
    department: "Finance",
    weight: 1.0,
  },
  {
    id: "shipping",
    name_vi: "Vận chuyển & Giao hàng",
    description: "Giao trễ, thất lạc",
    department: "Logistics",
    weight: 0.7,
  },
  {
    id: "product_quality",
    name_vi: "Chất lượng sản phẩm",
    description: "Lỗi sản phẩm",
    department: "QC Team",
    weight: 0.8,
  },
];

describe("ticketHelpers", () => {
  describe("resolvePriorityLevel", () => {
    it("prioritizes valid apiLevel over score thresholds", () => {
      expect(resolvePriorityLevel(10.0, "CRITICAL")).toBe("CRITICAL");
      expect(resolvePriorityLevel(95.0, "MEDIUM")).toBe("MEDIUM");
      expect(resolvePriorityLevel(88.0, "LOW")).toBe("LOW");
    });

    it("falls back to score thresholds when apiLevel is missing or unknown", () => {
      expect(resolvePriorityLevel(70.0)).toBe("CRITICAL");
      expect(resolvePriorityLevel(69.9, null)).toBe("MEDIUM");
      expect(resolvePriorityLevel(30.0, undefined)).toBe("MEDIUM");
      expect(resolvePriorityLevel(29.9, "UNKNOWN")).toBe("LOW");
    });
  });

  describe("FSM transitions", () => {
    it("mirrors backend StateManager transitions", () => {
      expect(ALLOWED_STATUS_TRANSITIONS).toEqual({
        new: ["assigned", "in_progress"],
        assigned: ["in_progress", "new"],
        in_progress: ["resolved", "assigned"],
        resolved: ["new"],
      });

      expect(canTransitionStatus("new", "new")).toBe(true);
      expect(canTransitionStatus("new", "assigned")).toBe(true);
      expect(canTransitionStatus("new", "in_progress")).toBe(true);
      expect(canTransitionStatus("new", "resolved")).toBe(false);

      expect(canTransitionStatus("assigned", "in_progress")).toBe(true);
      expect(canTransitionStatus("assigned", "new")).toBe(true);
      expect(canTransitionStatus("assigned", "resolved")).toBe(false);

      expect(canTransitionStatus("in_progress", "resolved")).toBe(true);
      expect(canTransitionStatus("in_progress", "assigned")).toBe(true);
      expect(canTransitionStatus("in_progress", "new")).toBe(false);

      expect(canTransitionStatus("resolved", "new")).toBe(true);
      expect(canTransitionStatus("resolved", "assigned")).toBe(false);
      expect(canTransitionStatus("resolved", "in_progress")).toBe(false);

      expect(canTransitionStatus("invalid", "new")).toBe(false);
    });
  });

  describe("evidence classification & highlighting", () => {
    it("keeps critical and high terms synced with backend rules and infers dynamic regex tiers from reason", () => {
      expect(CRITICAL_EVIDENCE_TERMS).toContain("charged twice");
      expect(CRITICAL_EVIDENCE_TERMS).toContain("double charged");
      expect(CRITICAL_EVIDENCE_TERMS).toContain("billed twice");
      expect(CRITICAL_EVIDENCE_TERMS).toContain("unauthorized charge");
      expect(HIGH_EVIDENCE_TERMS).toContain("refund");
      expect(HIGH_EVIDENCE_TERMS).toContain("hung up");
      expect(HIGH_EVIDENCE_TERMS).toContain("never arrived");
      expect(HIGH_EVIDENCE_TERMS).toContain("lost package");
      expect(HIGH_EVIDENCE_TERMS).toContain("stuck in transit");

      expect(getEvidenceLevel("  Charged Twice  ")).toBe("critical");
      expect(getEvidenceLevel("double charged")).toBe("critical");
      expect(getEvidenceLevel("chargeback")).toBe("critical");
      expect(getEvidenceLevel("never received")).toBe("high");
      expect(getEvidenceLevel("stuck in transit")).toBe("high");
      expect(getEvidenceLevel("refund")).toBe("high");
      expect(getEvidenceLevel("refund_payment")).toBe("aspect");

      expect(
        getEvidenceLevel("charged 5 times", "Từ khóa CRITICAL 'charged 5 times' ở câu kết: +30.0"),
      ).toBe("critical");
      expect(
        getEvidenceLevel("delayed for 3 weeks", "Từ khóa HIGH 'delayed for 3 weeks' ở câu #1: +10.0"),
      ).toBe("high");
      expect(
        getEvidenceLevel("hung up on me", "Từ khóa HIGH 'hung up on me' ở câu kết: +15.0"),
      ).toBe("high");
      expect(
        getEvidenceLevel(
          "refund_payment",
          "Khía cạnh nghiêm trọng nhất 'refund_payment' (trọng số 1.0, conf 0.95): +9.50",
        ),
      ).toBe("aspect");
    });

    it("detects Vietnamese backend reasons accurately without misclassifying aspect IDs", () => {
      expect(
        getEvidenceTone("Khía cạnh nghiêm trọng nhất 'refund_payment' (trọng số 1.0, conf 0.95): +9.50"),
      ).toBe("aspect");
      expect(getEvidenceTone("Cường độ câu cao (CAPS LOCK): +5.0")).toBe("intensity");
      expect(getEvidenceTone("Cú pháp câu chứa '!!!' (+5.0)")).toBe("intensity");
      expect(getEvidenceTone("Từ khóa CRITICAL 'charged twice' ở câu #1: +20.0")).toBe("urgency");
      expect(getEvidenceTone("AI phát hiện ngữ cảnh khẩn cấp CRITICAL (conf 0.85): +17.0")).toBe("urgency");
      expect(getEvidenceTone("Khủng hoảng đa khía cạnh (3 khía cạnh tiêu cực đồng thời): +15.0")).toBe("urgency");
      expect(getEvidenceTone("Cảm xúc tổng thể tiêu cực (0.95): base = 57.0")).toBe("sentiment");
    });

    it("highlights non-overlapping word-boundary evidence ranges including dynamic regex matches", () => {
      const content =
        "I had an issue, my parcel was delayed for 3 weeks, then I was charged 5 times! Please refund immediately before lawsuit.";
      const reasons = [
        "Từ khóa HIGH 'sue' ở câu #1: +10.0",
        "Từ khóa HIGH 'delayed for 3 weeks' ở câu #1: +10.0",
        "Từ khóa CRITICAL 'charged 5 times' ở câu #1: +20.0",
        "Từ khóa CRITICAL 'charged' ở câu #1: +20.0",
        "Từ khóa HIGH 'refund' ở câu kết: +15.0",
        "Từ khóa CRITICAL 'immediately' ở câu kết: +30.0",
      ];

      const ranges = findEvidenceRanges(content, reasons);
      expect(ranges.map((r) => [r.phrase, r.level])).toEqual([
        ["delayed for 3 weeks", "high"],
        ["charged 5 times", "critical"],
        ["refund", "high"],
        ["immediately", "critical"],
      ]);
    });
  });

  describe("taxonomy display & aspect matrix aggregation", () => {
    it("resolves Vietnamese aspect display names and falls back cleanly", () => {
      expect(getAspectDisplayName("refund_payment", SAMPLE_META)).toBe("Hoàn tiền & Thanh toán");
      expect(getAspectDisplayName("custom_topic", SAMPLE_META)).toBe("custom topic");
      expect(getAspectDisplayName("shipping")).toBe("shipping");
    });

    it("builds sorted multi-sentiment matrix from AspectStatItem[]", () => {
      const stats: AspectStatItem[] = [
        { aspect: "shipping", sentiment: "positive", count: 2 },
        { aspect: "shipping", sentiment: "negative", count: 8 },
        { aspect: "refund_payment", sentiment: "negative", count: 12 },
        { aspect: "refund_payment", sentiment: "neutral", count: 3 },
        { aspect: "product_quality", sentiment: "negative", count: 5 },
        { aspect: "product_quality", sentiment: "neutral", count: 5 },
      ];

      expect(buildAspectSentimentMatrix(stats, SAMPLE_META)).toEqual([
        {
          aspectId: "refund_payment",
          aspectName: "Hoàn tiền & Thanh toán",
          negative: 12,
          neutral: 3,
          positive: 0,
          total: 15,
        },
        {
          aspectId: "shipping",
          aspectName: "Vận chuyển & Giao hàng",
          negative: 8,
          neutral: 0,
          positive: 2,
          total: 10,
        },
        {
          aspectId: "product_quality",
          aspectName: "Chất lượng sản phẩm",
          negative: 5,
          neutral: 5,
          positive: 0,
          total: 10,
        },
      ]);
      expect(buildAspectSentimentMatrix([], SAMPLE_META)).toEqual([]);
    });
  });
});
