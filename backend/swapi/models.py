from django.db import models


class CsvFile(models.Model):
    filename = models.CharField(max_length=60)
    created_at = models.DateTimeField()

    class Meta:
        indexes = [
            models.Index(fields=['created_at'], name='idx_csv_file_created_at'),
            models.Index(fields=['filename'], name='idx_csv_file_filename'),
        ]

    def as_dict(self):
        return {"filename": self.filename, "created_at": self.created_at.timestamp()}
