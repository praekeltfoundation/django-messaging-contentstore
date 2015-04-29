from .models import Schedule, MessageSet, Message, BinaryContent
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from .serializers import (ScheduleSerializer, MessageSetSerializer,
                          MessageSerializer, BinaryContentSerializer,
                          MessageListSerializer)


class ScheduleViewSet(ModelViewSet):

    """
    API endpoint that allows Schedule models to be viewed or edited.
    """
    permission_classes = (IsAuthenticated,)
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer


class MessageSetViewSet(ModelViewSet):

    """
    API endpoint that allows MessageSet models to be viewed or edited.
    """
    permission_classes = (IsAuthenticated,)
    queryset = MessageSet.objects.all()
    serializer_class = MessageSetSerializer


class MessageViewSet(ModelViewSet):

    """
    API endpoint that allows Message models to be viewed or edited.
    """
    permission_classes = (IsAuthenticated,)
    queryset = Message.objects.all()
    serializer_class = MessageSerializer


class BinaryContentViewSet(ModelViewSet):

    """
    API endpoint that allows BinaryContent models to be viewed or edited.
    """
    permission_classes = (IsAuthenticated,)
    queryset = BinaryContent.objects.all()
    serializer_class = BinaryContentSerializer


class MessageSetMessagesList(ListAPIView):
    serializer_class = MessageListSerializer

    def get_queryset(self):
        """
        This view should return a list of all the messages
        for the supplied messageset.
        """
        messageset = self.kwargs['messageset']
        data = Message.objects.filter(messageset=messageset)
        return data
