# app/views.py
from rest_framework import generics, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from .models import UserProfile
from .serializers import UserProfileSerializer

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    def initial(self, request, *args, **kwargs):
        
        super().initial(request, *args, **kwargs)
    def get_object(self):
       
        
        profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
       
        return profile

    def perform_update(self, serializer):
         print("📷 Photo:", self.request.FILES.get("photo"))

         serializer.save(user=self.request.user)
    def perform_create(self, serializer):
       
        serializer.save(user=self.request.user)
