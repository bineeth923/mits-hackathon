from django.db.models import Max, Count
from django.utils import timezone

from bloodfinder.models import Donor, Request, BloodGroups, Donations

matrix_i = [BloodGroups.On, BloodGroups.Op, BloodGroups.Bn, BloodGroups.Bp, BloodGroups.An,
            BloodGroups.Ap, BloodGroups.ABn, BloodGroups.ABp]
matrix_j = matrix_i[::-1]

blood_match_matrix = [
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 1, 0, 1, 0, 1, 0],
    [1, 1, 0, 0, 1, 1, 0, 0],
    [1, 0, 0, 0, 1, 0, 0, 0],
    [1, 1, 1, 1, 0, 0, 0, 0],
    [1, 0, 1, 0, 0, 0, 0, 0],
    [1, 0, 0, 0, 0, 0, 0, 0],
]


class WeightedDonor:
    def __init__(self):
        self.donor = None
        self.weight = None


def get_blood_weight(target_group, current_group):
    if target_group == current_group:
        return 1
    i = matrix_i.index(target_group)
    j = matrix_j.index(current_group)
    if blood_match_matrix[i][j] == 1:
        return 0.75
    else:
        return 0


def get_weighted_donors(request: Request):
    district = request.district
    blood_group = request.blood_group
    weighted_list = []
    max_donations = Donations.objects.values('donor').annotate(count=Count('donor')).aggregate(Max('count'))['count__max']
    for d in Donor.objects.filter(district=district):
        w = WeightedDonor()
        w.weight = get_blood_weight(blood_group, d.blood_group)
        if w.weight == 0:
            continue
        if Donations.objects.filter(donor=d).filter(has_accepted=None).exists():
            continue
        if district == d.district:
            w.weight += 1
        else:
            continue
        if d.donations_set.filter(has_completed=True).last().request.time - timezone.now() < timezone.timedelta(weeks=12):
            continue
        else:
            w.weight /= (d.donations_set.filter(has_completed=True).last().request.time - timezone.now()).days
        w.weight += float(Donations.objects.filter(donor=d).aggregate(Count('id')))/float(max_donations)
        weighted_list.append(w)
    weighted_list.sort(key=(lambda x:x.weight))
    return weighted_list


def blood_rank(request: Request, top=3):
    weighted_list = get_weighted_donors(request)
    return weighted_list[:top]
