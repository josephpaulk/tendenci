def init_signals():
    from django.db.models.signals import post_save
    from tendenci.addons.locations.models import Location
    from tendenci.apps.contributions.signals import save_contribution

    post_save.connect(save_contribution, sender=Location, weak=False)