import time
from django.core.management.base import BaseCommand
from django.db.models import F
from shortner.models import ShortURL
from shortner.cache import redis_client, pop_pending_clicks


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        while True:
            keys = redis_client.scan_iter(match="clicks:*")

            for key in keys:
                code = key.replace("clicks:", "")
                count = pop_pending_clicks(code)

                if count > 0:
                    ShortURL.objects.filter(short_code=code).update(
                        click_count=F('click_count') + count
                    )
                    self.stdout.write(f"Flushed {count} clicks for {code}")

            time.sleep(60)