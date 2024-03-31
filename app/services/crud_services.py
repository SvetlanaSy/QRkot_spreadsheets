from app.core.utils import check_name_duplicate, check_full_amount
from app.crud.charityproject import charity_project_crud
from app.crud.donation import donation_crud
from app.models import Donation, CharityProject
from app.services.investing import investing, close_obj
from app.services.validators import check_charity_project_before_delete, check_charity_project_before_edit


class PreCRUDServices:

    def __init__(self, session):
        self.session = session

    async def update_partial_charity_project(self, project, obj_in):
        if obj_in.name != project.name:
            await check_name_duplicate(obj_in.name, self)
        if obj_in.full_amount != project.full_amount:
            check_full_amount(
                obj_in.full_amount, project.invested_amount)
        check_charity_project_before_edit(project)
        if project.full_amount == project.invested_amount:
            close_obj(project)
        project = await charity_project_crud.update(
            project, obj_in, self)
        return project

    async def remove_charity_project(self, project):
        check_charity_project_before_delete(
            project)
        await charity_project_crud.remove(
            project, self
        )
        return project

    async def create_full_charity_project(self, project):
        await check_name_duplicate(project.name, self)
        new_project = await charity_project_crud.create(self, project)
        new_project = await investing(self, new_project, Donation)
        return new_project

    async def create_full_donation(self, donation, user):
        new_donation = await donation_crud.create(
            self, donation, user)
        new_donation = await investing(self, new_donation, CharityProject)
        return new_donation
