from django.db import models, migrations
from django.contrib.postgres.operations import HStoreExtension, UnaccentExtension

class Migration(migrations.Migration):

    # dependencies = [
    #     ('main', '0001_initial'),
    # ]

    operations = [
        HStoreExtension(),
        UnaccentExtension()
    ]