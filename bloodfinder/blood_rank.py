from bloodfinder.models import Donor, Request, BloodGroups

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
    for d in Donor.objects.filter(district=district):
        blood_weight = get_blood_weight(blood_group, d.blood_group)
        if blood_weight == 0:
            continue


def blood_rank(request: Request, top=3):
    donor_list = []
    weighted_list = get_weighted_donors(request)
    return donor_list
