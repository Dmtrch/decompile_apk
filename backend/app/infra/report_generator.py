import json
import time

class ReportGenerator:
    def __init__(self):
        pass

    def generate_scorecard(self, static_results, dynamic_results):
        """Агрегирует результаты и рассчитывает Security Score"""
        findings = []
        
        # 1. Обработка SAST результатов
        sast_issues = static_results.get("sast", [])
        for issue in sast_issues:
            findings.append({
                "source": "SAST",
                "severity": issue.get("severity", "INFO"),
                "message": issue.get("message", "Unknown issue"),
                "location": issue.get("path", "N/A")
            })

        # 2. Обработка разрешений Манифеста
        manifest_issues = static_results.get("manifest", [])
        for issue in manifest_issues:
            findings.append({
                "source": "Manifest",
                "severity": "WARNING",
                "message": f"Dangerous permission: {issue.get('permission')}" if "permission" in issue else issue.get("issue"),
                "location": "AndroidManifest.xml"
            })

        # 3. Обработка DAST результатов
        for event in dynamic_results:
            severity = "HIGH" if "exfiltration" in event.get("type", "") else "INFO"
            findings.append({
                "source": "DAST",
                "severity": severity,
                "message": event.get("event"),
                "location": "Runtime"
            })

        # Расчет Score (базовая эвристика)
        score = 100
        high_risk_count = len([f for f in findings if f["severity"] == "HIGH"])
        warn_count = len([f for f in findings if f["severity"] == "WARNING"])
        
        score -= (high_risk_count * 20) + (warn_count * 5)
        score = max(0, score)

        return {
            "summary": {
                "security_score": score,
                "total_findings": len(findings),
                "high_risks": high_risk_count,
                "warnings": warn_count,
                "generated_at": time.ctime()
            },
            "findings": findings
        }
