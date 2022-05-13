import requests
from datetime import datetime, timedelta
from urllib.parse import quote_plus, urlencode, urljoin

from django.conf import settings
from django.utils import timezone

from rest_framework import status, views
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from safers.users.authentication import ProxyAuthentication
from safers.users.exceptions import AuthenticationException
from safers.users.permissions import IsRemote

from safers.data.models import DataType
from safers.data.serializers import DataLayerSerializer

_data_layer_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    example={
        "id": "1",
        "text": "Weather forecast",
        "info": "whatever",
        "children": [
          {
            "id": "1.1",
            "text": "Short term",
            "info": "whatever",
            "children": [
              {
                "id": "1.1.1",
                "text": "Temperature at 2m",
                "info": "whatever",
                "children": [
                  {
                    "id": "1.1.1.1",
                    "text": "2022-04-28T12:15:20Z",
                    "info_url": "http://localhost:8000/api/data/layers/metadata/02bae14e-c24a-4264-92c0-2cfbf7aa65f5",
                    "urls": [
                      "https://geoserver-test.safers-project.cloud/geoserver/ermes/wms?time=2022-04-28T12%3A15%3A20Z&layers=ermes%3A33101_t2m_33001_b7aa380a-20fc-41d2-bfbc-a6ca73310f4d&service=WMS&request=GetMap&srs=EPSG%3A4326&bbox={bbox}&width=256&height=256&format=image%2Fpng",
                      "https://geoserver-test.safers-project.cloud/geoserver/ermes/wms?time=2022-04-28T13%3A15%3A20Z&layers=ermes%3A33101_t2m_33001_b7aa380a-20fc-41d2-bfbc-a6ca73310f4d&service=WMS&request=GetMap&srs=EPSG%3A4326&bbox={bbox}&width=256&height=256&format=image%2Fpng",
                      "https://geoserver-test.safers-project.cloud/geoserver/ermes/wms?time=2022-04-28T14%3A15%3A20Z&layers=ermes%3A33101_t2m_33001_b7aa380a-20fc-41d2-bfbc-a6ca73310f4d&service=WMS&request=GetMap&srs=EPSG%3A4326&bbox={bbox}&width=256&height=256&format=image%2Fpng",
                    ]
                }
              ]
            }
          ]
        }
      ]
    }
)  # yapf: disable


_data_layer_list_schema = openapi.Schema(
    type=openapi.TYPE_ARRAY, items=_data_layer_schema
)  # yapf: disable


class DataLayerView(views.APIView):

    permission_classes = [IsAuthenticated, IsRemote]
    serializer_class = DataLayerSerializer

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        (If this were some type of ModelView, this fn would be built-in.)
        """

        return {
            'request': self.request, 'format': self.format_kwarg, 'view': self
        }

    def update_default_data(self, data):

        if data.pop("default_bbox") and "bbox" not in data:
            user = self.request.user
            default_bbox = user.default_aoi.geometry.extent
            data["bbox"] = ",".join(map(str, default_bbox))

        if data.pop("default_start") and "start" not in data:
            data["start"] = timezone.now() - timedelta(days=3)

        if data.pop("default_end") and "end" not in data:
            data["end"] = timezone.now()

        return data

    @swagger_auto_schema(
        query_serializer=DataLayerSerializer,
        responses={status.HTTP_200_OK: _data_layer_list_schema}
    )
    def get(self, request, *args, **kwargs):
        """
        Returns a hierarchy of available DataLayers. 
        Each leaf-node provides a URL paramter to retrieve the actual layer.
        """

        GATEWAY_URL_PATH = "/api/services/app/Layers/GetLayers"
        GEOSERVER_URL_PATH = "/geoserver/ermes/wms"
        METADATA_URL_PATH = "/api/data/layers/metadata"

        serializer = self.serializer_class(
            data=request.query_params,
            context=self.get_serializer_context(),
        )
        serializer.is_valid(raise_exception=True)

        updated_data = self.update_default_data(serializer.validated_data)
        proxy_params = {
            serializer.ProxyFieldMapping[k]: v
            for k, v in updated_data.items()
            if k in serializer.ProxyFieldMapping
        }  # yapf: disable

        try:
            response = requests.get(
                urljoin(settings.SAFERS_GATEWAY_API_URL, GATEWAY_URL_PATH),
                auth=ProxyAuthentication(request.user),
                params=proxy_params,
            )
            response.raise_for_status()
        except Exception as e:
            raise AuthenticationException(e)

        geoserver_query_params = urlencode(
            {
                "time": "{time}",
                "layers": "{name}",
                "service": "WMS",
                "request": "GetMap",
                "srs": "EPSG:4326",
                "bbox": "{bbox}",
                "width": 256,
                "height": 256,
                "format": "image/png",
            },
            safe="{}",
        )
        geoserver_url = f"{urljoin(settings.SAFERS_GEOSERVER_API_URL, GEOSERVER_URL_PATH)}?{geoserver_query_params}"

        metadata_url = f"{self.request.build_absolute_uri(METADATA_URL_PATH)}/{{metadata_id}}"

        data_type_info = {"None": None}
        data_type_info.update({
            data_type.datatype_id: data_type.description
            for data_type in DataType.objects.all()
        })

        content = response.json()

        data = [
          {
            "id": f"{i}",
            "text": group["group"],
            "info": None,
            "children": [
              {
                "id": f"{i}.{j}",
                "text": sub_group["subGroup"],
                "info": None,
                "children": [
                  {
                    "id": f"{i}.{j}.{k}",
                    "text": layer["name"],
                    "info": data_type_info.get(str(layer.get("dataTypeId"))),
                    "children": [
                      {
                        "id": f"{i}.{j}.{k}.{l}",
                        "text": detail["created_At"],
                        "info_url": metadata_url.format(metadata_id=detail.get("metadata_Id")),
                        "urls": [
                          geoserver_url.format(
                            name=quote_plus(detail["name"]),
                            time=quote_plus(timestamp),
                            bbox="{bbox}",
                          )
                          for timestamp in detail.get("timestamps", [])
                        ]
                      }
                      for l, detail in enumerate(
                        sorted(layer.get("details"), key=lambda x: x.get("created_At"), reverse=True) or [],
                        start=1
                      )
                      if l <= serializer.validated_data["n_layers"]
                    ]
                  }
                  for k, layer in enumerate(sub_group.get("layers") or [], start=1)
                ]
              }
              for j, sub_group in enumerate(group.get("subGroups") or [], start=1)
            ]
          } for i, group in enumerate(content.get("layerGroups") or [], start=1)
        ]  # yapf: disable

        return Response(data)


"""
SAMPLE PROXY DATA SHAPE:
{
  "layerGroups": [
    {
      "groupKey": "weather forecast",
      "group": "Weather forecast",
      "subGroups": [
        {
          "subGroupKey": "short term",
          "subGroup": "Short term",
          "layers": [
            {
              "dataTypeId": 33101,
              "group": "Weather forecast",
              "groupKey": "weather forecast",
              "subGroup": "Short term",
              "subGroupKey": "short term",
              "name": "Temperature at 2m",
              "partnerName": "FMI",
              "type": "Forecast",
              "frequency": "H6",
              "details": [
                {
                  "name": "ermes:33101_t2m_33001_78a8a797-fb5c-4b40-9f12-88a64fffc616",
                  "timestamps": [
                    "2022-04-05T01:00:00Z",
                    "2022-04-05T02:00:00Z",
                  ],
                  "created_At": "2022-04-05T07:10:30Z",
                  "request_Code": null,
                  "mapRequestCode": null,
                  "creator": null
                }  
              ]
            },
            {
              "dataTypeId": 35007,
              "group": "Environment",
              "groupKey": "environment",
              "subGroup": "Forecast",
              "subGroupKey": "forecast",
              "name": "Fire perimeter simulation as isochrones maps",
              "partnerName": "CIMA",
              "type": "Forecast",
              "frequency": "OnDemand",
              "details": [
                {
                  "name": "ermes:35007_85f6e495-c258-437d-a447-190742071807",
                  "timestamps": [
                    "2021-12-12T16:00:00"
                  ],
                  "created_At": "2022-03-10T12:14:43Z",
                  "request_Code": null,
                  "mapRequestCode": null,
                  "creator": null
                }
              ]
            },
            {
              "dataTypeId": 35008,
              "group": "Environment",
              "groupKey": "environment",
              "subGroup": "Forecast",
              "subGroupKey": "forecast",
              "name": "Mean fireline intensity",
              "partnerName": "CIMA",
              "type": "Forecast",
              "frequency": "OnDemand",
              "details": [
                {
                  "name": "ermes:35008_efc92e30-3333-408e-83bb-fcc43f6b3280",
                  "timestamps": [
                    "2021-12-12T16:00:00"
                  ],
                  "created_At": "2022-03-10T12:14:47Z",
                  "request_Code": null,
                  "mapRequestCode": null,
                  "creator": null
                }
              ]
            },
            {
              "dataTypeId": 35009,
              "group": "Environment",
              "groupKey": "environment",
              "subGroup": "Forecast",
              "subGroupKey": "forecast",
              "name": "Max fireline intensity",
              "partnerName": "CIMA",
              "type": "Forecast",
              "frequency": "OnDemand",
              "details": [
                {
                  "name": "ermes:35009_67576ad9-95c8-4736-9f28-cf4c13bc11bd",
                  "timestamps": [
                    "2021-12-12T16:00:00"
                  ],
                  "created_At": "2022-03-10T12:14:49Z",
                  "request_Code": null,
                  "mapRequestCode": null,
                  "creator": null
                }
              ]
            },
            {
              "dataTypeId": 35010,
              "group": "Environment",
              "groupKey": "environment",
              "subGroup": "Forecast",
              "subGroupKey": "forecast",
              "name": "Mean rate of spread",
              "partnerName": "CIMA",
              "type": "Forecast",
              "frequency": "OnDemand",
              "details": [
                {
                  "name": "ermes:35010_ae63de06-9161-4f9e-bcb1-1e1ebb215688",
                  "timestamps": [
                    "2021-12-12T16:00:00"
                  ],
                  "created_At": "2022-03-10T12:14:44Z",
                  "request_Code": null,
                  "mapRequestCode": null,
                  "creator": null
                }
              ]
            },
            {
              "dataTypeId": 35011,
              "group": "Environment",
              "groupKey": "environment",
              "subGroup": "Forecast",
              "subGroupKey": "forecast",
              "name": "Max rate of spread",
              "partnerName": "CIMA",
              "type": "Forecast",
              "frequency": "OnDemand",
              "details": [
                {
                  "name": "ermes:35011_42dcea6e-d4cd-4ba0-be9f-e79d576c6f82",
                  "timestamps": [
                    "2021-12-12T16:00:00"
                  ],
                  "created_At": "2022-03-10T12:14:46Z",
                  "request_Code": null,
                  "mapRequestCode": null,
                  "creator": null
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
"""