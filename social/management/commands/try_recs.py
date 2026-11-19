from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from social.recommendations import (
    FreindsLikedStrategy, GenresLikedStrategy, PopularStrategy, Recommender, seen_ids,
)

class Command(BaseCommand):
    help = "Print recommendations for a user, strategy by strategy"

    def add_arguments(self, parser):
        parser.add_argument("username")

    def handle(self, *args, **options):
        user = User.objects.get(username=options["username"])
        exclude = seen_ids(user)
        strategies = [FreindsLikedStrategy(), GenresLikedStrategy(), PopularStrategy()]

        for strategy in strategies:
            self.stdout.write(f"\n== {type(strategy).__name__} (weight {strategy.weight}) ==")
            for s in strategy.suggest(user, exclude, 5):
                self.stdout.write(f"  {s.score:.2f}  {s.book.title}  [{s.reason}]")

        self.stdout.write("\n== Combined ==")
        for e in Recommender(strategies).for_user(user, limit=10):
            self.stdout.write(f"  {e['score']:.2f}  {e['book'].title}  {e['reasons']}")