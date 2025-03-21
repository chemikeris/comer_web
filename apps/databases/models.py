from django.db import models

class ECOD(models.Model):
    uid = models.IntegerField(unique=True)
    ecod_domain_id = models.CharField(
        max_length=20, unique=True, db_collation='utf8_bin'
        )

    def __str__(self):
        return 'Domain: %s, UID: %09d' % (self.ecod_domain_id, self.uid)

