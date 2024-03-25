from datetime import datetime
from rest_framework import viewsets, status, serializers, permissions
from rest_framework.response import Response
from digestapi.models import Review, Book
from .books import BookSerializer  # Importing BookSerializer from your book module


class ReviewSerializer(serializers.ModelSerializer):

    is_owner = serializers.SerializerMethodField()

    def get_is_owner(self, obj):
        # Check if the user is the owner of the review
        return self.context["request"].user == obj.user

    class Meta:
        model = Review
        fields = ["id", "book", "user", "rating", "comment", "created_on", "is_owner"]


class ReviewViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    def list(self, request):
        reviews = Review.objects.all()
        serializer = ReviewSerializer(reviews, many=True, context={"request": request})
        return Response(serializer.data)

    def create(self, request):
        # Get data from request payload
        rating = request.data.get("rating")
        comment = request.data.get("comment")
        book_id = request.data.get("book_id")  # Fixing typo: "book id" to "book_id"

        # Create a new instance of Review
        try:
            book = Book.objects.get(pk=book_id)

            review = Review.objects.create(
                user=request.user,
                rating=rating,
                comment=comment,
                book_id=book_id,
                created_on=datetime.now(),  # Set the creation date/time
            )

            # Serialize the objects and pass request as context
            serializer = ReviewSerializer(review, context={"request": request})

            # Return the serialized data with 201 status code
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as ex:
            return Response(None, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        try:
            # Get the requested review
            review = Review.objects.get(pk=pk)

            # Serialize the object (make sure to pass the request as context)
            serializer = ReviewSerializer(review, context={"request": request})

            # Return the review with 200 status code
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Review.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, pk=None):
        try:
            # Get the requested review
            review = Review.objects.get(pk=pk)

            # Check if the user has permission to delete
            if review.user.id != request.user.id:
                return Response(status=status.HTTP_403_FORBIDDEN)

            # Delete the review
            review.delete()

            # Return success but no body
            return Response(status=status.HTTP_204_NO_CONTENT)

        except Review.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
