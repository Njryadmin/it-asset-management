from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import User, Category, Supplier, Department, Asset, AssetStatus
from app.core.security import get_password_hash
from app.core.database import AsyncSessionLocal, init_db
import asyncio


async def create_default_admin(db: AsyncSession):
    """Create default admin user"""
    result = await db.execute(select(User).where(User.username == "admin"))
    if not result.scalar_one_or_none():
        admin = User(
            username="admin",
            email="admin@example.com",
            full_name="系统管理员",
            hashed_password=get_password_hash("admin123"),
            is_superuser=True,
            is_active=True
        )
        db.add(admin)
        print("Created default admin user: admin / admin123")


async def create_sample_data(db: AsyncSession):
    """Create sample categories"""
    categories = [
        {"name": "计算机设备", "code": "COMPUTER", "description": "台式机、笔记本、服务器等"},
        {"name": "网络设备", "code": "NETWORK", "description": "路由器、交换机、防火墙等"},
        {"name": "办公设备", "code": "OFFICE", "description": "打印机、扫描仪、投影仪等"},
        {"name": "软件资产", "code": "SOFTWARE", "description": "操作系统、应用软件等"},
        {"name": "存储设备", "code": "STORAGE", "description": "硬盘、U盘、存储阵列等"},
    ]
    
    created_categories = []
    for cat_data in categories:
        result = await db.execute(select(Category).where(Category.code == cat_data["code"]))
        if not result.scalar_one_or_none():
            cat = Category(**cat_data)
            db.add(cat)
            created_categories.append(cat_data["name"])
    
    if created_categories:
        print(f"Created categories: {', '.join(created_categories)}")


async def create_sample_suppliers(db: AsyncSession):
    """Create sample suppliers"""
    suppliers = [
        {"name": "联想官方旗舰店", "code": "LENOVO", "contact_person": "张经理", "phone": "400-100-1234", "email": "business@lenovo.com"},
        {"name": "戴尔官方商城", "code": "DELL", "contact_person": "李经理", "phone": "400-888-8555", "email": "enterprise@dell.com"},
        {"name": "华为企业业务", "code": "HUAWEI", "contact_person": "王经理", "phone": "400-822-9999", "email": "enterprise@huawei.com"},
        {"name": "思科官方", "code": "CISCO", "contact_person": "John", "phone": "800-200-5555", "email": "cn-sales@cisco.com"},
    ]
    
    created = []
    for sup_data in suppliers:
        result = await db.execute(select(Supplier).where(Supplier.code == sup_data["code"]))
        if not result.scalar_one_or_none():
            sup = Supplier(**sup_data)
            db.add(sup)
            created.append(sup_data["name"])
    
    if created:
        print(f"Created suppliers: {', '.join(created)}")


async def create_sample_departments(db: AsyncSession):
    """Create sample departments"""
    departments = [
        {"name": "技术部", "code": "TECH", "description": "负责技术研发和系统维护"},
        {"name": "市场部", "code": "MARKETING", "description": "负责市场推广和品牌建设"},
        {"name": "销售部", "code": "SALES", "description": "负责产品销售和客户维护"},
        {"name": "财务部", "code": "FINANCE", "description": "负责财务管理和成本控制"},
        {"name": "人力资源部", "code": "HR", "description": "负责人员招聘和培训"},
    ]
    
    created = []
    for dept_data in departments:
        result = await db.execute(select(Department).where(Department.code == dept_data["code"]))
        if not result.scalar_one_or_none():
            dept = Department(**dept_data)
            db.add(dept)
            created.append(dept_data["name"])
    
    if created:
        print(f"Created departments: {', '.join(created)}")


async def init_sample_data():
    """Initialize sample data"""
    # First create all tables
    await init_db()
    # Then insert sample data
    async with AsyncSessionLocal() as db:
        try:
            await create_default_admin(db)
            await create_sample_data(db)
            await create_sample_suppliers(db)
            await create_sample_departments(db)
            await db.commit()
            print("Sample data initialization completed!")
        except Exception as e:
            print(f"Error initializing sample data: {e}")
            await db.rollback()


if __name__ == "__main__":
    asyncio.run(init_sample_data())
