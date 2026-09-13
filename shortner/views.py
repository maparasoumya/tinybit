from django.shortcuts import redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .cache import get_cached_url, set_cached_url, increment_click_counter, delete_cached_url, get_pending_clicks, check_rate_limit
from .serializers import ShortURLSerializer
from .models import ShortURL
from django.conf import settings
from .utils import generate_unique_short_code


class CreateURLView(APIView):
    def post(self, request):
        ip = request.META.get('REMOTE_ADDR')
        allowed, retry_after = check_rate_limit(ip)

        if not allowed:
            return Response(
                {"error": "Too many requests. Please try again later."},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
                headers={"Retry-After": str(retry_after)}
            )

        serializer = ShortURLSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        long_url = serializer.validated_data['long_url']
        custom_alias = request.data.get('custom_alias')

        if custom_alias:
            if ShortURL.objects.filter(short_code=custom_alias).exists():
                return Response(
                    {"error": "Alias already in use"},
                    status=status.HTTP_409_CONFLICT
                )
            short_code = custom_alias
        else:
            short_code = generate_unique_short_code()

        url_obj = ShortURL.objects.create(
            short_code=short_code,
            long_url=long_url
        )

        response_data = {
            "shortCode": url_obj.short_code,
            "shortUrl": f"{settings.BASE_URL}/{url_obj.short_code}",
            "longUrl": url_obj.long_url,
            "deleteToken": url_obj.delete_token,
            "createdAt": url_obj.created_at,
        }

        return Response(response_data, status=status.HTTP_201_CREATED)


class RedirectURLView(APIView):
    def get(self, request, code):
        cached_url = get_cached_url(code)

        if cached_url:
            print(f"CACHE HIT for {code}")
            increment_click_counter(code)
            return redirect(cached_url)

        print(f"CACHE MISS for {code}")
        try:
            url_obj = ShortURL.objects.get(short_code=code)
        except ShortURL.DoesNotExist:
            return Response(
                {"error": "Short code not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        set_cached_url(code, url_obj.long_url)
        increment_click_counter(code)

        return redirect(url_obj.long_url)


class URLDetailView(APIView):

    def get(self, request, code):
        try:
            url_obj = ShortURL.objects.get(short_code=code)
        except ShortURL.DoesNotExist:
            return Response(
                {"error": "Short Code Not Found"},
                status=status.HTTP_404_NOT_FOUND
            )

        total_clicks = url_obj.click_count + get_pending_clicks(code)

        response_data = {
            "shortCode": url_obj.short_code,
            "shortUrl": f"{settings.BASE_URL}/{url_obj.short_code}",
            "longUrl": url_obj.long_url,
            "clickCount": total_clicks,
            "createdAt": url_obj.created_at,
        }

        return Response(response_data, status=status.HTTP_200_OK)

    def delete(self, request, code):
        try:
            url_obj = ShortURL.objects.get(short_code=code)
        except ShortURL.DoesNotExist:
            return Response(
                {"error": "URL NOT FOUND"},
                status=status.HTTP_404_NOT_FOUND
            )
        provided_token = request.query_params.get('token')

        if provided_token != url_obj.delete_token:
            return Response(
                {"error": "Invalid or missing delete token"},
                status=status.HTTP_403_FORBIDDEN
            )

        url_obj.delete()
        delete_cached_url(code)

        return Response(status=status.HTTP_204_NO_CONTENT)