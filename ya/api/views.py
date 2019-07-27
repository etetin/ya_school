from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.decorators import permission_classes, api_view


@api_view(['POST', 'GET'])
@permission_classes((AllowAny,))
def test(request):
    response = {}

    return Response(response)