import os
import requests
from requests.auth import HTTPBasicAuth
import xml.etree.ElementTree as ET
from typing import Dict, List, Any

# SAP 설정 (운영 URL 고정)
SAP_USER = "INFPIUSR"
SAP_PASS = "http01"
NS = "http://hhi.co.kr/FI/XIMOB"

def _parse_xml_to_dict(element: ET.Element) -> Any:
    """XML 요소를 딕셔너리 또는 리스트로 변환하는 헬퍼 함수"""
    children = list(element)
    if not children:
        return element.text if element.text else ""
    
    # 동일한 태그가 여러 개 있으면 리스트로 처리
    if len(children) > 1 and len(set(c.tag for c in children)) == 1:
        return [_parse_xml_to_dict(c) for c in children]
    
    # 그렇지 않으면 딕셔너리로 처리
    res = {}
    for child in children:
        tag = child.tag
        if "}" in tag:  # Namespace 제거
            tag = tag.split("}")[1]
        
        parsed_val = _parse_xml_to_dict(child)
        
        # 중복 태그 처리 (다양한 태그가 섞여 있을 때)
        if tag in res:
            if not isinstance(res[tag], list):
                res[tag] = [res[tag]]
            res[tag].append(parsed_val)
        else:
            res[tag] = parsed_val
    return res

def _call_sap_soap(interface_id: str, body_content: str) -> Dict:
    """공통 SOAP 호출 함수"""
    url = f"http://hipop.hhi.co.kr:50000/XISOAPAdapter/MessageServlet?senderParty=&senderService=P_XIMOB&receiverParty=&receiverService=&interface={interface_id}_LEGY_SO&interfaceNamespace={NS}"
    
    soap_envelope = f"""<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ns="{NS}">
   <soapenv:Header/>
   <soapenv:Body>
      {body_content}
   </soapenv:Body>
</soapenv:Envelope>"""

    try:
        response = requests.post(
            url,
            data=soap_envelope.encode('utf-8'),
            headers={'Content-Type': 'text/xml;charset=UTF-8'},
            auth=HTTPBasicAuth(SAP_USER, SAP_PASS),
            timeout=30
        )
        response.raise_for_status()
        
        # XML 파싱
        root = ET.fromstring(response.text)
        body = root.find(".//{http://schemas.xmlsoap.org/soap/envelope/}Body")
        if body is not None and len(body) > 0:
            result_node = body[0]
            return _parse_xml_to_dict(result_node)
        return {}
    except Exception as e:
        print(f"[SOAP ERROR] {interface_id}: {e}")
        return {}

def call_xfi00250(params: dict) -> Dict:
    """카드 이용내역 및 카드 정보 조회"""
    inner_xml = f"""<ns:MT_XFI00250_LEGY>
         <PI_CARD_NUMC>{params.get('PI_CARD_NUMC', '')}</PI_CARD_NUMC>
         <PI_FR_DATE>{params.get('PI_FR_DATE', '')}</PI_FR_DATE>
         <PI_TO_DATE>{params.get('PI_TO_DATE', '')}</PI_TO_DATE>
         <PI_STATUS>{params.get('PI_STATUS', 'A')}</PI_STATUS>
         <PI_PERNR_O>{params.get('PI_PERNR_O', '')}</PI_PERNR_O>
         <PI_PERNR_R>{params.get('PI_PERNR_R', '')}</PI_PERNR_R>
         <PI_CALLSYS>{params.get('PI_CALLSYS', 'P')}</PI_CALLSYS>
      </ns:MT_XFI00250_LEGY>"""
    return _call_sap_soap("XFI00250", inner_xml)

def call_xfi00260(items: list) -> Dict:
    """비용처리 (전표 생성)"""
    item_xml = ""
    for it in items:
        item_xml += f"""
            <T_DATA>
               <BUKRS>{it.get('BUKRS','')}</BUKRS>
               <BUDAT>{it.get('BUDAT','')}</BUDAT>
               <CARD_NUMC>{it.get('CARD_NUMC','')}</CARD_NUMC>
               <APPR_DATE>{it.get('APPR_DATE','')}</APPR_DATE>
               <APPR_NUMC>{it.get('APPR_NUMC','')}</APPR_NUMC>
               <CANC_FLAG>{it.get('CANC_FLAG','')}</CANC_FLAG>
               <SEQN_NUMC>{it.get('SEQN_NUMC','')}</SEQN_NUMC>
               <DOCPR>{it.get('DOCPR','')}</DOCPR>
               <PERNR_O>{it.get('PERNR_O','')}</PERNR_O>
               <PERNR_R>{it.get('PERNR_R','')}</PERNR_R>
               <SGTXT>{it.get('SGTXT','')}</SGTXT>
               <MSG_TYPE></MSG_TYPE>
               <MSG_TXT></MSG_TXT>
            </T_DATA>"""
    
    inner_xml = f"<ns:MT_XFI00260_LEGY>{item_xml}</ns:MT_XFI00260_LEGY>"
    return _call_sap_soap("XFI00260", inner_xml)

def call_xfi00270(items: list) -> Dict:
    """처리취소 (전표 취소)"""
    item_xml = ""
    for it in items:
        item_xml += f"""
            <T_DATA>
               <BUKRS>{it.get('BUKRS','')}</BUKRS>
               <BELNR>{it.get('BELNR','')}</BELNR>
               <GJAHR>{it.get('GJAHR','')}</GJAHR>
               <CARD_NUMC>{it.get('CARD_NUMC','')}</CARD_NUMC>
               <APPR_DATE>{it.get('APPR_DATE','')}</APPR_DATE>
               <APPR_NUMC>{it.get('APPR_NUMC','')}</APPR_NUMC>
               <CANC_FLAG>{it.get('CANC_FLAG','')}</CANC_FLAG>
               <SEQN_NUMC>{it.get('SEQN_NUMC','')}</SEQN_NUMC>
               <PERNR>{it.get('PERNR','')}</PERNR>
               <MSG_TYPE></MSG_TYPE>
               <MSG_TXT></MSG_TXT>
            </T_DATA>"""
    inner_xml = f"<ns:MT_XFI00270_LEGY>{item_xml}</ns:MT_XFI00270_LEGY>"
    return _call_sap_soap("XFI00270", inner_xml)

def call_xfi00280(bukrs: str, pernr: str) -> Dict:
    """업무목록 조회"""
    inner_xml = f"""<ns:MT_XFI00280_LEGY>
         <PI_BUKRS>{bukrs}</PI_BUKRS>
         <PI_PERNR>{pernr}</PI_PERNR>
      </ns:MT_XFI00280_LEGY>"""
    return _call_sap_soap("XFI00280", inner_xml)

def call_xfi00290(params: dict) -> Dict:
    """예산 조회"""
    inner_xml = f"""<ns:MT_XFI00290_LEGY>
         <PI_BUKRS>{params.get('PI_BUKRS', '')}</PI_BUKRS>
         <PI_PERNR>{params.get('PI_PERNR', '')}</PI_PERNR>
         <PI_OBJNR>{params.get('PI_OBJNR', '')}</PI_OBJNR>
         <PI_OBJTY>{params.get('PI_OBJTY', '')}</PI_OBJTY>
         <PI_KSTAR>{params.get('PI_KSTAR', '')}</PI_KSTAR>
         <PI_GJAHR>{params.get('PI_GJAHR', '')}</PI_GJAHR>
         <I_SYSTEM>{params.get('I_SYSTEM', 'M')}</I_SYSTEM>
         <PI_CALLSYS>{params.get('PI_CALLSYS', 'P')}</PI_CALLSYS>
      </ns:MT_XFI00290_LEGY>"""
    return _call_sap_soap("XFI00290", inner_xml)

def call_xfi00310(params: dict) -> Dict:
    """연락처 조회"""
    inner_xml = f"""<ns:MT_XFI00310_LEGY>
         <PERNR>{params.get('PERNR', '')}</PERNR>
      </ns:MT_XFI00310_LEGY>"""
    return _call_sap_soap("XFI00310", inner_xml)

def call_xfi00320(params: dict) -> Dict:
    """공지사항 조회"""
    inner_xml = f"""<ns:MT_XFI00320_LEGY>
         <PERNR>{params.get('PERNR', '')}</PERNR>
      </ns:MT_XFI00320_LEGY>"""
    return _call_sap_soap("XFI00320", inner_xml)

