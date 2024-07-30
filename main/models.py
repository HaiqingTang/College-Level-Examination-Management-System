from django.db import models


# 管理员
class Admin(models.Model):
    count = models.CharField(max_length=256)  # 管理员账户
    password = models.CharField(max_length=256)  # 管理员密码


# 学生
class Student(models.Model):
    name = models.CharField(max_length=256)  # 学生姓名
    sid = models.CharField(max_length=256, primary_key=True)  # 学生学号
    password = models.CharField(max_length=256)  # 学生密码
    grade = models.CharField(max_length=256)  # 学生年级
    apartment = models.CharField(max_length=256)  # 学生学院
    major = models.CharField(max_length=256)  # 学生专业
    classes = models.CharField(max_length=256)  # 学生班级
    id = models.CharField(max_length=256)  # 学生身份证号
    stage = models.CharField(max_length=256)  # 学生学历层次
    email = models.EmailField()  # 学生邮箱
    phone = models.IntegerField()  # 学生电话


# 监考老师
class Teacher(models.Model):
    name = models.CharField(max_length=256)  # 监考姓名
    tid = models.CharField(max_length=256)  # 监考工号
    password = models.CharField(max_length=256)  # 监考密码
    identity = models.CharField(max_length=256)  # 监考身份证号
    apartment = models.CharField(max_length=256)  # 监考学院
    phone = models.IntegerField()  # 监考电话
    email = models.EmailField(max_length=256)  # 监考老师的邮箱


# 考试类别表
class TestClass(models.Model):
    name = models.CharField(max_length=256)  # 考试类别名
    id = models.AutoField(primary_key=True)  # 考试类别编号


# 考试批次表
class TestBatch(models.Model):
    name = models.CharField(max_length=256)  # 批次名
    test_class = models.ForeignKey(TestClass, on_delete=models.CASCADE)
    startTime = models.DateField()  # 考试开始时间
    endTime = models.DateField()  # 考试结束时间
    date = models.DateField()  # 考试日期
    time = models.CharField(max_length=256, default="9:00")  # 考试时间
    state = models.CharField(max_length=64)  # 启用状态


# 考场表
class TestRoom(models.Model):
    test_batch = models.ForeignKey(TestBatch, on_delete=models.CASCADE)
    area = models.CharField(max_length=256)  # 考试地点
    MaxNum = models.IntegerField()  # 考场最大人数
    CurrentNum = models.IntegerField()  # 考场当前人数


# 考场-教师表
class TestTeacher(models.Model):
    test_room = models.ForeignKey(TestRoom, on_delete=models.CASCADE)
    test_teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)


# 考场-学生表
class TestStudent(models.Model):
    test_room = models.ForeignKey(TestRoom, on_delete=models.CASCADE)
    test_student = models.ForeignKey(Student, on_delete=models.CASCADE)
    photo = models.FileField(upload_to='photo')  # 学生报名后上传的照片
    pay = models.CharField(max_length=256, default="0")  # 是否付款


# 成绩表
class Score(models.Model):
    score = models.CharField(max_length=256)  # 学生成绩
    student_id = models.CharField(max_length=256, default="0")  # 学生
    test_room_id = models.CharField(max_length=256, default="0")  # 考场
