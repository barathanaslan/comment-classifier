tarih_schema = {
  "$schema": "http://json-schema.org/draft-04/schema#",
  "type": "object",
  "properties": {
    "tarih": {
      "type": "string",
      "maxLength": 10,
      "pattern": "[2][0][12][0-9][-][01][0-9][-][0-3][0-9]",
      "description": "Yorumlarını görmek istediğiniz günün tarihini yazınız. Örnek: 2003-07-15"
    }
  },
  "required": [
    "tarih"
  ]
}

comment_schema = {
  "$schema": "http://json-schema.org/draft-04/schema#",
  "type": "object",
  "properties": {
    "comment": {
      "type": "string"
    }
  },
  "required": [
    "comment"
  ]
}

creating_comment_schema = {
  "$schema": "http://json-schema.org/draft-04/schema#",
  "type": "object",
  "properties": {
    "ogrenci_id": {
      "type": "integer"
    },
    "ders_id": {
      "type": "integer"
    },
    "secenek_id": {
      "type": "integer"
    },
    "icerik_id": {
      "type": "integer"
    },
    "sorun": {
      "type": "string"
    },
    "durum": {
      "type": "integer",
      "patters": "[01]"
    },
    "tip": {
      "type": "string"
    },
    "mobil": {
      "type": "integer",
      "patters": "[01]"
    }
  },
  "required": [
    "ogrenci_id",
    "ders_id",
    "secenek_id",
    "icerik_id",
    "sorun",
    "durum",
    "tip",
    "mobil"
  ]
}
