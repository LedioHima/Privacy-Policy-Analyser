# analyzer/risk_patterns.py
# ─────────────────────────────────────────────────────────────────────────────
# The keyword dictionary — the academic core of Week 2.
#
# This module defines all 7 RiskCategory objects, each containing a list of
# RiskPattern regex patterns. This is the only file that needs to be updated
# when adding new detection rules.
#
# Design principles:
#   - Patterns are case-insensitive (applied to lowercased text)
#   - Patterns use word boundaries (\b) to avoid partial-word false positives
#   - {0,N} quantifiers keep matches local to one clause, not the whole sentence
#   - Each category has a `weight` that drives the risk score algorithm
#
# Severity guide:
#   HIGH   -- Direct user harm: data sold, location tracked, no deletion right
#   MEDIUM -- Indirect harm: behavioral profiling, law enforcement sharing
# ─────────────────────────────────────────────────────────────────────────────

from .models import RiskPattern, RiskCategory

RISK_CATEGORIES: list[RiskCategory] = [

    # ── 1. Data Selling & Third-Party Sharing ────────────────────────────────
    RiskCategory(
        name="Data Selling & Third-Party Sharing",
        description="The company sells or shares your personal data with external parties.",
        weight=25,
        patterns=[
            RiskPattern(
                r"\bsell\b.{0,40}\b(data|information|profile|records)\b",
                "This policy explicitly states they may SELL your personal data.",
                "HIGH"
            ),
            RiskPattern(
                r"\bshare\b.{0,60}\b(third.part|partner|affiliate|advertis)",
                "Your data is shared with third-party partners, likely for advertising.",
                "HIGH"
            ),
            RiskPattern(
                r"\b(transfer|disclose|provide).{0,50}\b(third.part|outside|external)",
                "Your data may be transferred or disclosed to outside organizations.",
                "HIGH"
            ),
            RiskPattern(
                r"\bmonetize\b.{0,40}\b(data|information|user)",
                "The company explicitly monetizes (makes money from) your data.",
                "HIGH"
            ),
            RiskPattern(
                r"\badvertising partner|marketing partner|data broker",
                "Your data is shared with advertising or data broker networks.",
                "HIGH"
            ),
            RiskPattern(
                r"\bshare.{0,40}\bfor (marketing|advertising|commercial)",
                "Your data is shared specifically for marketing or advertising purposes.",
                "HIGH"
            ),
        ]
    ),

    # ── 2. Location Tracking ─────────────────────────────────────────────────
    RiskCategory(
        name="Location Tracking",
        description="The company collects your physical location data.",
        weight=20,
        patterns=[
            RiskPattern(
                r"\b(precise|exact|real.time|continuous).{0,30}\b(location|gps|geolocation)",
                "Your precise or real-time GPS location is being tracked.",
                "HIGH"
            ),
            RiskPattern(
                r"\bcollect.{0,40}\b(location|gps|geolocation|coordinates)",
                "The company collects your location data.",
                "HIGH"
            ),
            RiskPattern(
                r"\btrack.{0,40}\b(location|movement|whereabouts|physical)",
                "Your physical movements or whereabouts may be tracked.",
                "HIGH"
            ),
            RiskPattern(
                r"\b(ip address|wi.fi|bluetooth).{0,40}\b(location|infer|derive|estimate)",
                "Your location is inferred from your IP address, Wi-Fi, or Bluetooth signals.",
                "MEDIUM"
            ),
            RiskPattern(
                r"\bgeofenc|location.based service|location history",
                "The company uses geofencing or stores your location history.",
                "HIGH"
            ),
        ]
    ),

    # ── 3. Indefinite Data Retention ─────────────────────────────────────────
    RiskCategory(
        name="Indefinite Data Retention",
        description="The company keeps your data indefinitely or for vague time periods.",
        weight=20,
        patterns=[
            RiskPattern(
                r"\bretain.{0,50}\b(as long as (necessary|needed|required)|indefinitely|forever)",
                "Your data is kept for an undefined or unlimited period of time.",
                "HIGH"
            ),
            RiskPattern(
                r"\bkeep.{0,50}\b(as long as|until|indefinitely|no set|no specific)",
                "There is no clear deletion schedule — data may be kept indefinitely.",
                "HIGH"
            ),
            RiskPattern(
                r"\bno.{0,20}(expir|delet|remov).{0,30}(schedul|date|polic)",
                "There is no expiration or scheduled deletion policy for your data.",
                "HIGH"
            ),
            RiskPattern(
                r"\barchiv.{0,40}\b(indefinitely|permanently|long.term)",
                "Your data is archived permanently or for the long term.",
                "MEDIUM"
            ),
            RiskPattern(
                r"\bretention period.{0,40}(not|no|undefined|unspecified|varies)",
                "The data retention period is unspecified or varies without clear rules.",
                "HIGH"
            ),
        ]
    ),

    # ── 4. No Right to Deletion ──────────────────────────────────────────────
    RiskCategory(
        name="No Right to Deletion",
        description="Users cannot delete their account or request data removal.",
        weight=20,
        patterns=[
            RiskPattern(
                r"\bcannot.{0,40}\b(delete|remove|erase).{0,30}\b(account|data|information)",
                "You are explicitly told you CANNOT delete your data or account.",
                "HIGH"
            ),
            RiskPattern(
                r"\bno.{0,20}(right|option|ability).{0,30}\b(delet|remov|eras)",
                "There is no right or option provided to delete your data.",
                "HIGH"
            ),
            RiskPattern(
                r"\b(waive|forfeit|relinquish).{0,40}\b(right|claim).{0,30}\b(data|privacy|delet)",
                "You are asked to waive your data rights, including the right to deletion.",
                "HIGH"
            ),
            RiskPattern(
                r"\bdeletion request.{0,40}(may be denied|not guaranteed|not obligated)",
                "Deletion requests may be denied without clear reason.",
                "HIGH"
            ),
            RiskPattern(
                r"\bsome (data|information).{0,40}(cannot|may not).{0,30}(be deleted|be removed)",
                "Some of your data cannot be deleted even if you request it.",
                "HIGH"
            ),
        ]
    ),

    # ── 5. Behavioral Profiling ──────────────────────────────────────────────
    RiskCategory(
        name="Behavioral Profiling",
        description="The company builds personal profiles based on your behavior and activity.",
        weight=15,
        patterns=[
            RiskPattern(
                r"\b(build|creat|develop|maintain).{0,40}\b(profile|profil)",
                "The company builds a behavioral profile about you.",
                "MEDIUM"
            ),
            RiskPattern(
                r"\b(track|monitor|record).{0,40}\b(browsing|behavior|activity|habit|interest)",
                "Your browsing behavior, habits, and interests are being tracked.",
                "MEDIUM"
            ),
            RiskPattern(
                r"\binfer.{0,40}\b(interest|preference|characteristic|attribute)",
                "The company makes inferences about your personality or interests.",
                "MEDIUM"
            ),
            RiskPattern(
                r"\bbehavioral.{0,30}(advertis|target|data|analytic)",
                "You are targeted with behavioral advertising based on tracked activity.",
                "MEDIUM"
            ),
            RiskPattern(
                r"\b(cross.site|cross.platform|cross.device).{0,30}(track|monitor|follow)",
                "Your activity is tracked across multiple websites, platforms, or devices.",
                "HIGH"
            ),
            RiskPattern(
                r"\bfingerprint(ing)?.{0,30}(device|browser|user)",
                "Your device or browser is fingerprinted to identify you without cookies.",
                "HIGH"
            ),
        ]
    ),

    # ── 6. Children's Data Collection ────────────────────────────────────────
    RiskCategory(
        name="Children's Data Collection",
        description="The company collects data from or about children under 13.",
        weight=25,
        patterns=[
            RiskPattern(
                r"\b(collect|process|use).{0,50}\b(child|minor|under.13|under 13|coppa)",
                "The policy addresses data collection from children — requires careful review.",
                "HIGH"
            ),
            RiskPattern(
                r"\bchild(ren)?.{0,40}(data|information|privacy)",
                "The company handles children's data — check if proper safeguards exist.",
                "HIGH"
            ),
            RiskPattern(
                r"\bunder.{0,10}(13|sixteen|18|eighteen).{0,30}(collect|use|share|data)",
                "Data is collected from users under a certain age — a legal red flag.",
                "HIGH"
            ),
            RiskPattern(
                r"\bparental consent.{0,40}(not required|may not|waived)",
                "Parental consent requirements may not be enforced for minors.",
                "HIGH"
            ),
        ]
    ),

    # ── 7. Law Enforcement & Government Sharing ──────────────────────────────
    RiskCategory(
        name="Law Enforcement & Government Sharing",
        description="The company shares your data with government agencies or law enforcement.",
        weight=15,
        patterns=[
            RiskPattern(
                r"\b(law enforcement|government|authorit|agenc).{0,50}\b(request|demand|order|require)",
                "Your data may be handed over to law enforcement or government agencies on request.",
                "MEDIUM"
            ),
            RiskPattern(
                r"\b(share|disclose|provide).{0,50}\b(law enforcement|government|court|legal process)",
                "Data is disclosed to courts, law enforcement, or in legal proceedings.",
                "MEDIUM"
            ),
            RiskPattern(
                r"\b(subpoena|court order|legal obligation|national security)",
                "Data can be shared under subpoena, court order, or national security requests.",
                "MEDIUM"
            ),
            RiskPattern(
                r"\bwithout.{0,30}(notice|notif|warrant|your knowledge)",
                "Your data can be shared with authorities without notifying you.",
                "HIGH"
            ),
            RiskPattern(
                r"\bvoluntarily.{0,40}\b(share|cooperat|assist).{0,30}(government|law enforcement|authorit)",
                "The company voluntarily assists government agencies beyond legal requirements.",
                "HIGH"
            ),
        ]
    ),
]
