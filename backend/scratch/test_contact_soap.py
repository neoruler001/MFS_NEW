import sys
import os

# backend 디렉토리를 path에 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.soap_client import call_xfi00310

def test():
    # 로그에서 확인한 사번 사용
    params = {"PERNR": "A509166"}
    print(f"Calling SAP for PERNR: {params['PERNR']}")
    result = call_xfi00310(params)
    import json
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    test()
