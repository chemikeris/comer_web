from django.db import models


# UniProt data
class UniProt(models.Model):
    uniprot_ac = models.CharField(
        max_length=20, unique=True, db_collation='utf8_bin'
        )
    annotation = models.TextField(db_collation='utf8_bin')


# PDB data tables
class PDB(models.Model):
    id = models.CharField(
        max_length=20, unique=True, db_collation='utf8_bin', primary_key=True
        )


class PDBAnnotation(models.Model):
    annotation = models.TextField(db_collation='utf8_bin', unique=True)


class Chain(models.Model):
    pdb = models.ForeignKey(PDB, on_delete=models.CASCADE)
    chain = models.CharField(max_length=20, db_collation='utf8_bin')
    annotation = models.ForeignKey(PDBAnnotation, on_delete=models.RESTRICT,
                                   null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['pdb', 'chain'],
                name='unique_pdb_chain'
                ),
            ]


# ECOD data
class ECODAnnotation(models.Model):
    A = 1
    X = 2
    H = 3
    T = 4
    F = 5
    ecod_hierarchy_variants = (
        (A, 'A',),
        (X, 'X',),
        (H, 'H',),
        (T, 'T',),
        (F, 'F',)
        )
    ecod_hierarchy = models.IntegerField(choices=ecod_hierarchy_variants)
    name = models.TextField(db_collation='utf8_bin')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['ecod_hierarchy', 'name'],
                name='unique_ecod_annotation'
                ),
            ]


class ECOD(models.Model):
    uid = models.IntegerField(unique=True)
    ecod_domain_id = models.CharField(
        max_length=20, unique=True, db_collation='utf8_bin'
        )
    pdb_chain = models.ForeignKey(Chain, on_delete=models.RESTRICT, null=True)
    annotations = models.ManyToManyField(ECODAnnotation)
    
    def __str__(self):
        return 'Domain: %s, UID: %09d' % (self.ecod_domain_id, self.uid)


# SCOPe data
class SCOP(models.Model):
    domain_id = models.CharField(
        max_length=20, unique=True, db_collation='utf8_bin'
        )
    annotation = models.TextField(db_collation='utf8_bin')

