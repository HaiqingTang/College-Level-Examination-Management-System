from main.models import *
from django.shortcuts import render, redirect, reverse
import random
import pandas as pd
import csv
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError
import chardet
import openpyxl
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from .pay import AliPay
import uuid
from urllib.parse import parse_qs
from datetime import datetime
import time

global_pay = None


# 验证是否登录
def user_is_login(request):
    uid = request.COOKIES.get('uid')
    suid = request.session.get('uid', 'noId')
    is_login = request.session.get('is_login', False)
    if (str(uid) == str(suid) and is_login == True):
        return True
    else:
        return False


# 登录
def login(request):
    if request.method == "GET":
        return render(request, 'login/index.html')
    elif request.method == "POST":
        role_name = request.POST.get("roleName")
        account_num = request.POST.get("accountNum")
        password = request.POST.get("password")
        try:
            student = Student.objects.get(sid=account_num)
            if not Student.objects.filter(sid=account_num).exists():
                return render(request, 'login/index.html', {"msg": "账号不存在"})
            elif Student.objects.get(sid=account_num).password != password:
                return render(request, 'login/index.html', {"msg": "密码错误"})
            else:
                student_homepage_html = redirect(reverse("student_homepage"))
                uid = account_num
                student_homepage_html.set_cookie("uid", uid, max_age=3600 * 24 * 7)
                request.session.set_expiry(3600 * 24 * 7)
                request.session['uid'] = uid
                request.session['is_login'] = True
                return student_homepage_html
        except Student.DoesNotExist:
            try:
                teacher = Teacher.objects.get(tid=account_num)
                if not Teacher.objects.filter(tid=account_num).exists():
                    return render(request, 'login/index.html', {"msg": "账号不存在"})
                elif Teacher.objects.get(tid=account_num).password != password:
                    return render(request, 'login/index.html', {"msg": "密码错误"})
                else:
                    teacher_homepage_html = redirect(reverse("teacher_homepage"))
                    uid = account_num
                    teacher_homepage_html.set_cookie("uid", uid, max_age=3600 * 24 * 7)
                    request.session.set_expiry(3600 * 24 * 7)
                    request.session['uid'] = uid
                    request.session['is_login'] = True
                    return teacher_homepage_html
            except Teacher.DoesNotExist:
                try:
                    admin = Admin.objects.get(count=account_num)
                    if not Admin.objects.filter(count=account_num).exists():
                        return render(request, 'login/index.html', {"msg": "账号不存在"})
                    elif Admin.objects.get(count=account_num).password != password:
                        return render(request, 'login/index.html', {"msg": "密码错误"})
                    else:
                        teacher_homepage_html = redirect(reverse("admin_homepage"))
                        uid = account_num
                        teacher_homepage_html.set_cookie("uid", uid, max_age=3600 * 24 * 7)
                        request.session.set_expiry(3600 * 24 * 7)
                        request.session['uid'] = uid
                        request.session['is_login'] = True
                        return teacher_homepage_html
                except Admin.DoesNotExist:
                    print("用户不存在")

        # if role_name == "学生":
        #     if not Student.objects.filter(sid=account_num).exists():
        #         return render(request, 'login/index.html', {"msg": "账号不存在"})
        #     elif Student.objects.get(sid=account_num).password != password:
        #         return render(request, 'login/index.html', {"msg": "密码错误"})
        #     else:
        #         student_homepage_html = redirect(reverse("student_homepage"))
        #         uid = account_num
        #         student_homepage_html.set_cookie("uid", uid, max_age=3600 * 24 * 7)
        #         request.session.set_expiry(3600 * 24 * 7)
        #         request.session['uid'] = uid
        #         request.session['is_login'] = True
        #         return student_homepage_html
        # elif role_name == "监考老师":
        #     if not Teacher.objects.filter(tid=account_num).exists():
        #         return render(request, 'login/index.html', {"msg": "账号不存在"})
        #     elif Teacher.objects.get(tid=account_num).password != password:
        #         return render(request, 'login/index.html', {"msg": "密码错误"})
        #     else:
        #         teacher_homepage_html = redirect(reverse("teacher_homepage"))
        #         uid = account_num
        #         teacher_homepage_html.set_cookie("uid", uid, max_age=3600 * 24 * 7)
        #         request.session.set_expiry(3600 * 24 * 7)
        #         request.session['uid'] = uid
        #         request.session['is_login'] = True
        #         return teacher_homepage_html
        # elif role_name == "管理员":
        #     if not Admin.objects.filter(count=account_num).exists():
        #         return render(request, 'login/index.html', {"msg": "账号不存在"})
        #     elif Admin.objects.get(count=account_num).password != password:
        #         return render(request, 'login/index.html', {"msg": "密码错误"})
        #     else:
        #         teacher_homepage_html = redirect(reverse("admin_homepage"))
        #         uid = account_num
        #         teacher_homepage_html.set_cookie("uid", uid, max_age=3600 * 24 * 7)
        #         request.session.set_expiry(3600 * 24 * 7)
        #         request.session['uid'] = uid
        #         request.session['is_login'] = True
        #         return teacher_homepage_html


# 学生的主页
def student_homepage(request):
    if request.method == "GET":

        if user_is_login(request):
            uid = request.COOKIES.get('uid')
            student = Student.objects.get(sid=uid)
            return render(request, "student/homepage/index.html", {"student": student, "identity": "学生"})
        else:
            return redirect(reverse("login"), {"msg": "请先登录！"})


# 学生的信息
def stuinfo(request):
    if request.method == "GET":

        if user_is_login(request):
            uid = request.COOKIES.get('uid')
            student = Student.objects.get(sid=uid)
            return render(request, "student/info/myinfo.html", {"student": student, "identity": "学生"})
        else:
            return redirect(reverse("login"), {"msg": "请先登录！"})


# 学生修改信息
def stuChangeInfo(request):
    if request.method == "GET":

        if user_is_login(request):
            uid = request.COOKIES.get('uid')
            student = Student.objects.get(sid=uid)
            return render(request, "student/info/changeinfo.html", {"student": student, "identity": "学生"})
        else:
            return redirect(reverse("login"), {"msg": "请先登录！"})
    if request.method == "POST":
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        uid = request.COOKIES.get('uid')
        student = Student.objects.get(sid=uid)
        student.phone = phone
        student.email = email
        student.save()

        return render(request, "student/info/myinfo.html", {"student": student, "identity": "学生"})


# 学生报考
def regist(request):
    if request.method == "GET":
        if user_is_login(request):
            testbatch = TestBatch.objects.all()
            uid = request.COOKIES.get('uid')
            student = Student.objects.get(sid=uid)

            return render(request, "student/regist.html",
                          {"testbatch": testbatch, "student": student, "identity": "学生"})
        else:

            return redirect(reverse("login"), {"msg": "请先登录！"})
    if request.method == "POST":
        return render(request, "student/regist.html", )


# 学生报考信息
def registPost(request, batchId):
    if request.method == "GET":
        if user_is_login(request):
            uid = request.COOKIES.get('uid')
            student = Student.objects.get(sid=uid)
            photo = ""
            batch = TestBatch.objects.get(id=batchId)


            for room_student in TestStudent.objects.filter(test_student=student):
                if room_student.test_room.test_batch.id == batchId:
                    photo = room_student.photo

            student = Student.objects.get(sid=uid)
            return render(request, "student/registPost.html", {"student": student,
                                                               "photo": photo, "batch": batch, "identity": "学生"})
        else:
            return redirect(reverse("login"), {"msg": "请先登录！"})
    if request.method == "POST":
        if "submitBaomingbiao" in request.POST:
            uid = request.COOKIES.get('uid')

            student = Student.objects.get(sid=uid)
            email = request.POST.get("email")
            phone = request.POST.get("phone")
            batch = TestBatch.objects.get(id=batchId)
            print("22", batch.name, batch.date, batch.time)
            student.email = email
            student.phone = phone
            testroom = TestRoom.objects.filter(test_batch=batch)
            room = []
            for t in testroom:
                room.append(t.id)
            print("room", room)
            room_id = random.choice(room)  # 随机获取一个教室

            ts = TestStudent(test_room=TestRoom.objects.get(id=room_id), test_student=student,
                             photo=request.FILES.get("photo"), pay="0")
            ts.save()
            global global_pay
            global_pay = ts.id
            print("global_pay", global_pay)
            return render(request, "student/registPost.html", {"student": student,
                                                               "photo": ts.photo, "message": "pay", "batch": batch,
                                                               "identity": "学生"})
        return render(request, "student/registPost.html", )


# 学生考试信息
def searchStu(request):
    if request.method == "GET":
        if user_is_login(request):
            uid = request.COOKIES.get('uid')
            student = Student.objects.get(sid=uid)
            test = TestStudent.objects.filter(test_student=student)
            testList = []
            for t in test:
                test = t.test_room
                testbatch = test.test_batch
                testList.append({
                    "pay": t.pay,
                    "batch": testbatch.name,
                    "date": testbatch.date,
                    "classes": testbatch.test_class.name,
                    "name": student.name,
                    "apartment": student.apartment,
                    "major": student.major

                })

            return render(request, "student/searchStu.html",
                          {"testList": testList, "student": student, "identity": "学生"})
        else:

            return redirect(reverse("login"), {"msg": "请先登录！"})
    if request.method == "POST":
        classes = request.POST.get('classes')
        t1 = TestClass(name=classes)
        t1.save()
        allclasses = TestClass.objects.all()
        return render(request, "student/searchStu.html", {"allclasses": allclasses})


# 学生考试信息
def gradeShow(request):
    if request.method == "GET":
        if user_is_login(request):
            ave1 = 88
            ave2 = 92
            ave3 = 70
            ave4 = 82
            return render(request, "student/homepage/gradeShow.html",
                          {'ave1': ave1, 'ave2': ave2, 'ave3': ave3, 'ave4': ave4, "identity": "学生"})
        else:

            return redirect(reverse("login"), {"msg": "请先登录！"})
    if request.method == "POST":
        return render(request, "student/homepage/gradeShow.html")


# 学生查看数据
def dataShow(request):
    if request.method == "GET":
        if user_is_login(request):

            return render(request, "student/dataShow.html")
        else:

            return redirect(reverse("login"), {"msg": "请先登录！"})
    if request.method == "POST":
        return render(request, "student/dataShow.html")


# 监考的主页
def teacher_homepage(request):
    if request.method == "GET":
        if user_is_login(request):
            uid = request.COOKIES.get('uid')
            teacher = Teacher.objects.get(tid=uid)
            return render(request, "teacher/homepage.html", {"teacher": teacher, "identity": "监考人员"})
        else:
            return redirect(reverse("login"), {"msg": "请先登录！"})


# 管理员的主页
def admin_homepage(request):
    if request.method == "GET":
        if user_is_login(request):
            # id = "1"
            # name = "name"
            # t1 = TestClass.objects.get(id=id)
            # t1.name = "newName"
            # t1.save()
            return render(request, "admin/homepage/index.html")
        else:
            return redirect(reverse("login"), {"msg": "请先登录！"})


# 新建考试类
def admin_newClass(request):
    if request.method == "GET":
        if user_is_login(request):
            allclasses = TestClass.objects.all()

            return render(request, "admin/newTest/newClass.html", {"allclasses": allclasses})
        else:

            return redirect(reverse("login"), {"msg": "请先登录！"})
    if request.method == "POST":
        if "new" in request.POST:
            classes = request.POST.get('classes')
            t1 = TestClass(name=classes)
            t1.save()
            allclasses = TestClass.objects.all()
            return render(request, "admin/newTest/newClass.html", {"allclasses": allclasses})
        if "delete" in request.POST:
            cid = request.POST.get('cid')
            print(cid)
            t = TestClass.objects.get(id=cid)
            print(t)
            t.delete()

            allclasses = TestClass.objects.all()

            return render(request, "admin/newTest/newClass.html", {"allclasses": allclasses})
        allclasses = TestClass.objects.all()
        return render(request, "admin/newTest/newClass.html", {"allclasses": allclasses})


# 新建考试批次
def admin_newBanch(request):
    if request.method == "GET":
        if user_is_login(request):
            batch = TestBatch.objects.all()
            allclasses = TestClass.objects.all()
            # 获取当前时间
            now = datetime.now()
            now_date = now.date()
            for b in batch:
                if now_date > b.date:
                    b.state = "已完成"
                    b.save()
                else:
                    b.state = "未完成"
                    b.save()

            return render(request, "admin/newTest/newBanch.html", {"batch": batch, "allclasses": allclasses})
        else:

            return redirect(reverse("login"), {"msg": "请先登录！"})
    if request.method == "POST":
        if "new" in request.POST:
            testClass = request.POST.get('testClass')
            grade = request.POST.get('grade')
            startTime = request.POST.get('startTime')
            endTime = request.POST.get('endTime')
            date = request.POST.get('date')
            state = request.POST.get('state')
            name = testClass + grade
            cid = TestClass.objects.get(name=testClass)
            batch1 = TestBatch(name=name, startTime=startTime, endTime=endTime, date=date, state=state, test_class=cid)

            batch1.save()

        if "delete" in request.POST:
            cid = request.POST.get('cid')

            t = TestBatch.objects.get(id=cid)

            t.delete()

        batch = []
        for b in TestBatch.objects.all():
            batch.append({
                "testClassName": b.test_class.name,
                "id": b.id,
                "name": b.name,
                "startTime": b.startTime,
                "endTime": b.endTime,
                "date": b.date,
                "state": b.state,

            })
        return render(request, "admin/newTest/newBanch.html", {"batch": batch})


# 新建考试场次
def admin_newTest(request):
    if request.method == "GET":
        if user_is_login(request):
            room = TestRoom.objects.all()
            batch = TestBatch.objects.all()

            return render(request, "admin/newTest/newTest.html", {"room": room, "batch": batch})
        else:

            return redirect(reverse("login"), {"msg": "请先登录！"})
    if request.method == "POST":
        if "new" in request.POST:
            testBatch = request.POST.get('batch')
            TestB = TestBatch.objects.get(name=testBatch)

            room = request.POST.get('room')
            date = request.POST.get('date')
            cnum = request.POST.get('cnum')
            mnum = request.POST.get('mnum')

            test1 = TestRoom(area=room, MaxNum=mnum, CurrentNum=cnum, test_batch=TestB)

            test1.save()
            room = TestRoom.objects.all()
            batch = TestBatch.objects.all()
            return render(request, "admin/newTest/newTest.html", {"room": room, "batch": batch})

        if "xiugai" in request.POST:
            TestBatchId = request.POST.get("id")
            area = request.POST.get("area")
            cnum = request.POST.get("CNum")
            mnum = request.POST.get("MNum")

            t = TestRoom.objects.get(id=TestBatchId)
            t.area = area
            t.CurrentNum = cnum
            t.MaxNum = mnum
            t.save()
            room = TestRoom.objects.all()
            batch = TestBatch.objects.all()
            return render(request, "admin/newTest/newTest.html", {"room": room, "batch": batch})
        if "delete" in request.POST:
            tid = request.POST.get('id')
            t = TestRoom.objects.get(id=tid)
            t.delete()

            room = TestRoom.objects.all()
            batch = TestBatch.objects.all()
            return render(request, "admin/newTest/newTest.html", {"room": room, "batch": batch})

        return render(request, "admin/newTest/newTest.html")


# 批次查看学生
def admin_banchStudent(request):
    if request.method == "GET":
        if user_is_login(request):
            return render(request, "admin/student/banch_student.html")
        else:

            return redirect(reverse("login"), {"msg": "请先登录！"})
    if request.method == "POST":
        return render(request, "admin/student/banch_student.html")


# 查看一批考试的学生
def admin_testStudent(request):
    if request.method == "GET":
        if user_is_login(request):
            Test = TestBatch.objects.all()
            return render(request, "admin/student/test_student.html", {"Test": Test})
        else:

            return redirect(reverse("login"), {"msg": "请先登录！"})
    if request.method == "POST":
        if "delete" in request.POST:
            id1 = request.POST.get("id1")
            t = TestStudent.objects.get(id=id1)
            t.delete()

        if "change" in request.POST:
            id1 = request.POST.get("id")
            phone = request.POST.get("phone")
            email = request.POST.get("email")
            t = TestStudent.objects.get(id=id1)
            student = t.test_student

            student.phone = phone
            student.email = email
            student.save()

        Test = TestBatch.objects.all()
        batch_name = request.POST.get('batch')
        batch = TestBatch.objects.get(name=batch_name)
        testInfo = []
        for room in TestRoom.objects.filter(test_batch=batch):
            for stu_room in TestStudent.objects.filter(test_room=room):
                testInfo.append({
                    "id": stu_room.id,
                    "testbatch": stu_room.test_room.test_batch.name,
                    "testClass": stu_room.test_room.test_batch.test_class.name,
                    "pay": stu_room.pay,
                    "stuName": stu_room.test_student.name,
                    "stuSid": stu_room.test_student.sid,
                    "stuStage": stu_room.test_student.stage,
                    "stuGrade": stu_room.test_student.grade,
                    "stuApartment": stu_room.test_student.apartment,
                    "stuMajor": stu_room.test_student.major,
                    "stuClasses": stu_room.test_student.classes,
                    "stuID": stu_room.test_student.id,
                    "stuPhone": stu_room.test_student.phone,
                    "stuEmail": stu_room.test_student.email,
                    "testDate": stu_room.test_room.test_batch.date,
                    "testRoom": stu_room.test_room.area,

                })

        return render(request, "admin/student/test_student.html", {"testInfo": testInfo, "Test": Test})


# 查看所有学生
def admin_allStudent(request):
    if request.method == "GET":
        if user_is_login(request):

            student = Student.objects.all()
            return render(request, "admin/student/allStudent.html",
                          {"Student": student})
        else:

            return redirect(reverse("login"), {"msg": "请先登录！"})
    if request.method == "POST":
        return render(request, "admin/student/allStudent.html")


# 查看所有监考
def admin_allTeacher(request):
    if request.method == "GET":
        if user_is_login(request):

            teacher = Teacher.objects.all()
            return render(request, "admin/teacher/allTeacher.html",
                          {"Teacher": teacher})
        else:

            return redirect(reverse("login"), {"msg": "请先登录！"})
    if request.method == "POST":
        if "change" in request.POST:
            tid = request.POST.get("tid")
            name = request.POST.get("name")
            id1 = request.POST.get("id")
            apartment = request.POST.get("apartment")
            phone = request.POST.get("phone")
            email = request.POST.get("email")

            t = Teacher.objects.get(tid=tid)
            t.name = name
            t.id1 = id1
            t.apartment = apartment
            t.phone = phone
            t.email = email
            t.save()
            teacher = Teacher.objects.all()
            return render(request, "admin/teacher/allTeacher.html",
                          {"Teacher": teacher})
        if "delete" in request.POST:
            tid = request.POST.get("tid")
            t = Teacher.objects.get(tid=tid)
            t.delete()

            teacher = Teacher.objects.all()
            return render(request, "admin/teacher/allTeacher.html",
                          {"Teacher": teacher})
        teacher = Teacher.objects.all()
        return render(request, "admin/teacher/allTeacher.html", {"Teacher": teacher})


# 批次查看监考
def admin_batchTeacher(request):
    if request.method == "GET":
        if user_is_login(request):
            Test = TestBatch.objects.all()
            teacher = Teacher.objects.all()
            batch = TestBatch.objects.get(name="日语考试N2")
            test_room = TestRoom.objects.filter(test_batch=batch)
            return render(request, "admin/teacher/batch_teacher.html",
                          {"Test": Test, "Teacher": teacher, "test_room": test_room})
        else:

            return redirect(reverse("login"), {"msg": "请先登录！"})
    if request.method == "POST":
        if "search" in request.POST:
            batch_name = request.POST.get('batch')

            batch = TestBatch.objects.get(name=batch_name)
            test_room = TestRoom.objects.filter(test_batch=batch)

            Test = TestBatch.objects.all()
            teacher = Teacher.objects.all()
            test_teacher = TestTeacher.objects.all()
            state = "未分配监考"
            for t in test_room:
                for testT in test_teacher:

                    if testT.test_room == t:
                        state = "已分配监考"

            return render(request, "admin/teacher/batch_teacher.html",
                          {"Test": Test, "Teacher": teacher, "test_room": test_room, "batch": batch, "state": state,
                           "batchName": batch_name})

        if "select" in request.POST:

            batch_name = request.POST.get('batchName')
            teacher = Teacher.objects.all()
            name = []
            for t in teacher:
                if t.name in request.POST:
                    name.append(t.name)
            print(batch_name)
            batch = TestBatch.objects.get(name=batch_name)  # 筛选该批次的所有考试教室

            testRoom = TestRoom.objects.filter(test_batch=batch)

            n = len(name)  # 列表长度

            for t in testRoom:
                a = random.sample(name, 1)
                print(name)
                print(f"选出的数为: {a}", a)
                teacher = Teacher.objects.filter(name=a[0])
                print(teacher)
                name.remove(a[0])
                t1 = TestTeacher(test_room=t, test_teacher=teacher[0])
                t1.save()
                testt = TestTeacher.objects.all()
                print(testt)

            Test = TestBatch.objects.all()
            teacher = Teacher.objects.all()
            batch = TestBatch.objects.get(name="日语考试N2")
            test_room = TestRoom.objects.filter(test_batch=batch)
            return render(request, "admin/teacher/batch_teacher.html",
                          {"Test": Test, "Teacher": teacher, "test_room": test_room})

        # # 随机分配监考
        # n = len(name)  # 列表长度
        # while n > 0:
        #     if n == 1:
        #         print(f"最后一个数: {name[0]}")
        #         break
        #     # a, b = random.sample(name, 2)
        #     # print(f"选出的两个数为: {a}, {b}")
        #     # name.remove(a)
        #     # name.remove(b)
        #     # n -= 2
        #     a= random.sample(name, 1)
        #     print(f"选出的两个数为: {a}")
        #     name.remove(a)
        #     n -= 1

        return render(request, "admin/teacher/batch_teacher.html")


# 管理员查看学生成绩
def scoreManage(request):
    if request.method == "GET":
        if user_is_login(request):
            score = Score.objects.all()
            scoreList = []
            for s in score:
                test_room = TestRoom.objects.get(id=s.test_room_id)
                student = Student.objects.get(sid=s.student_id)
                scoreList.append({
                    "score": s.score,
                    "batch": test_room.test_batch.name,
                    "date": test_room.test_batch.date,
                    "class": test_room.test_batch.test_class.name,
                    "name": student.name,
                    "sid": student.sid,
                    "grade": student.grade,
                    "classes": student.classes,
                    "id": student.id,
                    "stage": student.stage,
                    "phone": student.phone,
                    "email": student.email,
                    "apartment": student.apartment,
                    "major": student.major

                })

            return render(request, "admin/student/scoreManage.html", {"scoreList": scoreList})
        else:

            return redirect(reverse("login"), {"msg": "请先登录！"})
    if request.method == "POST":
        return render(request, "admin/student/scoreManage.html")


def watchTeacher(request):
    if request.method == "GET":
        if user_is_login(request):
            uid = request.COOKIES.get('uid')
            teacher = Teacher.objects.get(tid=uid)
            testteacher = TestTeacher.objects.filter(test_teacher=teacher)
            ret = []
            for room in testteacher:
                ret.append({
                    "batch": room.test_room.test_batch.name,
                    "test_class": room.test_room.test_batch.test_class.name,
                    "date": room.test_room.test_batch.date,
                    "time": room.test_room.test_batch.time,
                    "room": room.test_room.area,
                    "num": room.test_room.CurrentNum,
                    "max_num": room.test_room.MaxNum,

                })

            return render(request, "teacher/watch_teacher.html", {"ret": ret, "teacher": teacher})
        else:

            return redirect(reverse("login"), {"msg": "请先登录！"})
    if request.method == "POST":
        uid = request.COOKIES.get('uid')
        testroom = TestTeacher.objects.filter(test_teacher=uid)
        print(testroom)

        return render(request, "teacher/watch_teacher.html")


# 监考查看考试
def teacher_test(request):
    if request.method == "GET":
        if user_is_login(request):
            uid = request.COOKIES.get('uid')
            testroom = TestTeacher.objects.filter(test_teacher=uid)
            print(testroom)

            ret = []
            # for room in testroom:
            #     for teacher in TestTeacher.objects.filter(test_room=room):
            #         ret.append({
            #             "kaoci": batch.name,
            #             "test_class": batch.test_class.name,
            #             "date": batch.date,
            #             "room": room.area,
            #             "num": room.CurrentNum,
            #             "max_num": room.MaxNum,
            #             "teacher": teacher.test_teacher.name,
            #         })

            return render(request, "admin/newTest/newClass.html", {"ret": ret})
        else:

            return redirect(reverse("login"), {"msg": "请先登录！"})
    if request.method == "POST":
        classes = request.POST.get('classes')
        t1 = TestClass(name=classes)
        t1.save()
        allclasses = TestClass.objects.all()
        return render(request, "admin/newTest/newClass.html", {"allclasses": allclasses})


# 监考的信息
def teainfo(request):
    if request.method == "GET":

        if user_is_login(request):
            uid = request.COOKIES.get('uid')
            teacher = Teacher.objects.get(tid=uid)
            return render(request, "teacher/teainfo.html", {"teacher": teacher})
        else:
            return redirect(reverse("login"), {"msg": "请先登录！"})


# 监考修改信息
def teaChangeInfo(request):
    if request.method == "GET":

        if user_is_login(request):
            uid = request.COOKIES.get('uid')
            teacher = Teacher.objects.get(tid=uid)
            return render(request, "teacher/changeTeaInfo.html", {"teacher": teacher})
        else:
            return redirect(reverse("login"), {"msg": "请先登录！"})
    if request.method == "POST":
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        uid = request.COOKIES.get('uid')
        teacher = Teacher.objects.get(tid=uid)
        teacher.phone = phone
        teacher.email = email
        teacher.save()

        return render(request, "teacher/teainfo.html", {"teacher": teacher})


@csrf_exempt
def upload_file(request):
    if request.method == "GET":
        if user_is_login(request):
            uid = request.COOKIES.get('uid')
            return render(request, "admin/student/upload.html")
        else:

            return redirect(reverse("login"), {"msg": "请先登录！"})

    if request.method == 'POST':
        # 获取传递过来的文件和数据库名
        uploaded_file = request.FILES['file']
        database_name = request.POST.get('database')

        # 打开上传的文件
        wb = openpyxl.load_workbook(uploaded_file)

        # 获取指定表格数据
        ws = wb['Sheet1']
        rows = []
        for row in ws.iter_rows(min_row=2, values_only=True):
            rows.append(list(row))

        # 关闭文件
        wb.close()
        print(rows)

        # 根据数据库名进行不同的数据操作
        if database_name == 'students':
            # 将学生数据写入数据库
            for row in rows:
                try:
                    student = Student(name=row[0], sid=row[1], password=row[2], grade=row[3], apartment=row[4],
                                      major=row[5], classes=row[6], id=row[7], stage=row[8], email=row[9],
                                      phone=row[10])

                    student.full_clean()
                    student.save()
                except ValidationError as e:
                    print("数据格式错误")
                    return JsonResponse({'error': '数据格式错误：' + str(e)}, status=400)
            return JsonResponse({'message': '导入成功！'})

        elif database_name == 'invigilators':
            # 将监考数据写入数据库
            for row in rows:
                try:
                    invigilator = Teacher(name=row[0], tid=row[1], password=row[2],
                                          identity=row[3], apartment=row[4], phone=row[5], email=row[6])
                    invigilator.full_clean()
                    invigilator.save()
                except ValidationError as e:
                    return JsonResponse({'error': '数据格式错误：' + str(e)}, status=400)
            return JsonResponse({'message': '导入成功！'})

        elif database_name == 'scores':
            # 将成绩数据写入数据库
            for row in rows:
                try:
                    score = Score(score=row[0], student_id=row[1], test_room_id=row[2])
                    score.full_clean()
                    score.save()
                except ValidationError as e:
                    return JsonResponse({'error': '数据格式错误：' + str(e)}, status=400)
            return JsonResponse({'message': '导入成功！'})

        else:
            return JsonResponse({'error': '无效的数据库名！'}, status=400)

    else:
        return JsonResponse({'error': '只允许使用 POST 请求！'}, status=405)


# 学生查看成绩
def grade(request):
    if request.method == "GET":
        if user_is_login(request):
            uid = request.COOKIES.get('uid')
            score = Score.objects.filter(student_id=uid)
            student = Student.objects.get(sid=uid)
            scoreList = []
            for s in score:
                test_room = TestRoom.objects.get(id=s.test_room_id)

                scoreList.append({
                    "score": s.score,
                    "batch": test_room.test_batch.name,
                    "class": test_room.test_batch.test_class.name,
                    "name": student.name,
                    "sid": student.sid,
                    "apartment": student.apartment,
                    "major": student.major

                })

            return render(request, "student/grade.html", {"scoreList": scoreList})
        else:

            return redirect(reverse("login"), {"msg": "请先登录！"})
    if request.method == "POST":
        return render(request, "student/grade.html")


# 删除学生信息
def deleteStuInfo(request):
    if request.method == "POST":
        sid = request.POST.get('sid')
        student = Student(sid=sid)
        room = request.POST.get('testroom')
        print(sid, room)
        # testroom = TestRoom(id=room)
        testroom = TestStudent(test_student=student, test_room=room)
        # testroom.delete()
        # testroom.save()
        #
        # batch_name = request.POST.get('batch')
        # print(batch_name)
        # batch = TestBatch.objects.get(name=batch_name)
        # testInfo = []
        # for room in TestRoom.objects.filter(test_batch=batch):
        #     for stu_room in TestStudent.objects.filter(test_room=room):
        #         testInfo.append({
        #
        #             "testbatch": stu_room.test_room.test_batch.name,
        #             "testClass": stu_room.test_room.test_batch.test_class.name,
        #             "stuName": stu_room.test_student.name,
        #             "stuSid": stu_room.test_student.sid,
        #             "stuStage": stu_room.test_student.stage,
        #             "stuGrade": stu_room.test_student.grade,
        #             "stuApartment": stu_room.test_student.apartment,
        #             "stuMajor": stu_room.test_student.major,
        #             "stuClasses": stu_room.test_student.classes,
        #             "testDate": stu_room.test_room.test_batch.date,
        #             "testRoom": stu_room.test_room.area,
        #
        #         })
        #         print(stu_room.test_student.name)

        # return render(request, "admin/student/test_student.html", {"testInfo": testInfo})
        return render(request, "admin/student/test_student.html")

    if request.method == "GET":
        return render(request, "admin/student/test_student.html")


# 支付
def pay(request):
    return render(request, 'pay.html')


def dingdan(request):
    # 实例化AliPay
    alipay = AliPay(
        appid="2021000122693122",
        app_notify_url='http://127.0.0.1:8000/check/',  # 支付宝会向这个地址发送post请求
        return_url='http://127.0.0.1:8000/show/',  # 支付宝会向这个地址发送get请求
        app_private_key_path=r'D:\thq\ExamManagement\static\rsakey\private2048.txt',  # 应用私钥
        alipay_public_key_path=r'D:\thq\ExamManagement\static\rsakey\paypublic.txt',  # 支付宝公钥
        debug=True,  # 默认是False
    )
    print("dingdan")
    # 定义请求地址传入的参数
    res = alipay.direct_pay(
        subject='考试费用',  # 商品描述
        out_trade_no=str(uuid.uuid4()),  # 订单号
        total_amount='140',  # 交易金额(单位是元，保留两位小数)
    )
    # 生成跳转到支付宝支付页面的url
    url = 'https://openapi.alipaydev.com/gateway.do?{0}'.format(res)
    return redirect(url)


def show(request):
    if request.method == 'GET':
        alipay = AliPay(
            appid="2021000122693122",
            app_notify_url='http://127.0.0.1:8000/check/',
            return_url='http://127.0.0.1:8000/show/',
            app_private_key_path=r'D:\thq\ExamManagement\static\rsakey\private2048.txt',  # 应用私钥
            alipay_public_key_path=r'D:\thq\ExamManagement\static\rsakey\paypublic.txt',  # 支付宝公钥
            debug=True,  # 默认是False
        )
        print("show")
        param = request.GET.dict()  # 获取请求携带的参数并转换成字典类型
        sign = param.pop('sign', None)  # 获取sign的值
        # 对sign参数进行验证
        statu = alipay.verify(param, sign)
        if statu:
            global global_pay
            ts = TestStudent.objects.get(id=global_pay)

            ts.pay = "1"

            ts.save()
            uid = request.COOKIES.get('uid')
            student = Student.objects.get(sid=uid)
            return render(request, "student/homepage/index.html",
                          {"student": student, "identity": "学生", 'msg': '支付成功'})

        else:
            return render(request, 'show.html', {'msg': '支付失败'})
    else:
        return render(request, 'show.html', {'msg': '只支持GET请求，不支持其它请求'})


def check(request):
    if request.method == 'POST':
        alipay = AliPay(appid="2021000122693122",
                        app_notify_url='http://127.0.0.1:8000/check/',  # 支付宝会向这个地址发送post请求
                        return_url='http://127.0.0.1:8000/show_msg/',  # 支付宝会向这个地址发送get请求
                        app_private_key_path=r'D:\thq\ExamManagement\static\rsakey\private2048.txt',
                        # 应用私钥
                        alipay_public_key_path=r'D:\thq\ExamManagement\static\rsakey\paypublic.txt',
                        # 支付宝公钥
                        debug=True,
                        )
        print("check")

        body = request.body.decode('utf-8')  # 转成字符串
        post_data = parse_qs(body)  # 根据&符号分割
        post_dict = {}
        for k, v in post_data.items():
            post_dict[k] = v[0]
        sign = post_dict.pop('sign', None)
        status = alipay.verify(post_dict, sign)
        if status:  # 支付成功

            return HttpResponse('支付成功')
        else:
            return HttpResponse('支付失败')
    else:
        return HttpResponse('只支持POST请求')


def dropdown(request):
    if request.method == "GET":
        return render(request, "admin/newTest/dropdown.html")
