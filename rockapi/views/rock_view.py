from django.http import HttpResponseServerError
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from django.contrib.auth.models import User
from rockapi.models import Rock, Type

class RockView(ViewSet):
    """Rock view set"""


    def create(self, request):
        """Handle POST operations

        Returns:
            Response -- JSON serialized instance
        """

        chosen_type = Type.objects.get(pk=request.data['typeId'])

        rock = Rock()
        rock.user = request.auth.user
        rock.weight = request.data['weight']
        rock.name = request.data['name']
        rock.type = chosen_type
        rock.save()

        serialized = RockSerializer(rock, many=False)

        return Response(serialized.data, status=status.HTTP_201_CREATED)

    def list(self, request):
        """Handle GET requests for all items

        Returns:
            Response -- JSON serialized array
        """

        owner_only = self.request.query_params.get("owner", None)

        try:
            rocks = Rock.objects.all()

            # If `?owner=current` is in the URL
            if owner_only is not None and owner_only == "current":
                # Filter to only the current user's rocks
                rocks = rocks.filter(user=request.auth.user)

            serializer = RockSerializer(rocks, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as ex:
            return HttpResponseServerError(ex)
        
    def destroy(self, request, pk=None):
        """Handle DELETE requests for a single item

        Returns:
            Response -- 200, 404, or 500 status code
        """
            
        try:
            rock = Rock.objects.get(pk=pk)

            if rock.user.id == request.auth.user.id:   
                rock.delete()
                return Response(None, status=status.HTTP_204_NO_CONTENT)
            else: 
                return Response({'message': 'You do not have permission to delete this rock.'}, status=status.HTTP_403_FORBIDDEN)

        except Rock.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RockTypeSerializer(serializers.ModelSerializer):
    """JSON serializer"""

    class Meta:
        model = Type
        fields = ('label',)

class RockOwnerSerializer(serializers.ModelSerializer):
    """JSON serializer"""

    class Meta:
        model = User
        fields = ('first_name', 'last_name')


class RockSerializer(serializers.ModelSerializer):
    """JSON serializer"""

    type = RockTypeSerializer(many=False)
    user = RockOwnerSerializer(many=False)

    class Meta:
        model = Rock
        fields = ( 'id', 'name', 'weight', 'user', 'type',)
