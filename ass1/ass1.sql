-- comp3311 22T1 Assignment 1

-- Q1
create or replace view Q1(unswid, name)
as
--... SQL statements, possibly using other views/functions defined by you ...
Select unswid, name
From People
Join (
	Select DistinctStu.student As studentId
	From (
		Select student, Count(Distinct program) As numProgram
		From Program_enrolments
		Group By student
	) As DistinctStu
	Where DistinctStu.numProgram > 4
) As disCourseStu
On disCourseStu.studentId = People.id
;


-- Q2
create or replace view Q2(unswid, name, course_cnt)
as
--... SQL statements, possibly using other views/functions defined by you ...
With tutorCourses As (
	Select unswid, name, course_cnt
	From People
	Join (
		Select Tutors.tutor as tutorId, Count(course) As course_cnt
		From (
			Select staff As tutor, Course_staff.course
			From Course_staff
			Where Course_staff.role
				= 
				(Select id From Staff_roles Where Staff_roles.name = 'Course Tutor')
		) As Tutors
		Group By Tutors.tutor
	) As tutorCourseCnt
	On tutorCourseCnt.tutorId = People.id
)
Select unswid, name, course_cnt
From tutorCourses
Where course_cnt 
	= 
	(Select max(course_cnt) 
	From tutorCourses
	)
;


-- Q3
create or replace view Q3(unswid, name)
as
--... SQL statements, possibly using other views/functions defined by you ...
Select Distinct unswid, name
From People 
Join (
	Select Course_enrolments.student As studentId
	From Courses 
	Join (
		Select id as subjectId
		From Subjects
		Where offeredBy 
			=
			(Select OrgUnits.id
			From OrgUnits
			Where OrgUnits.name = 'School of Law')
	) As lawSubject
	On Courses.subject = lawSubject.subjectId
	Join Course_enrolments
	On Course_enrolments.course = Courses.id
	Where Course_enrolments.mark > 85
) As lawStu
On People.id = studentId
Join (
	Select id As intlStuId
	From Students
	Where stype = 'intl'
) As intlStu
On People.id = intlStuId
;


-- Q4
create or replace view Q4(unswid, name)
as
--... SQL statements, possibly using other views/functions defined by you ...
Select unswid, name
From People
Join(
Select Distinct c9020.student As studId
From (Select student, term
	From Course_enrolments
	Join (
		Select id As courseId, term
		From Courses
		Where Courses.subject 
			=  
			(Select id
			From Subjects
			Where Subjects.code = 'COMP9020'
			)
	) As comp9020
	On Course_enrolments.course = comp9020.courseId
	) As c9020
	Join (
	Select student, term
	From Course_enrolments
	Join (
		Select id As courseId, term
		From Courses
		Where Courses.subject 
			=  
			(Select id
			From Subjects
			Where Subjects.code = 'COMP9331'
			)
	) As comp9331
	On Course_enrolments.course = comp9331.courseId
	) As c9331
	On c9020.term = c9331.term And c9020.student = c9331.student
) As courseStu
On People.id = courseStu.studId
Join (
	Select id As localStuId
	From Students
	Where stype = 'local'
) As localStu
On People.id = localStuId
;


-- Q5a
create or replace view Q5a(term, min_fail_rate)
as
--... SQL statements, possibly using other views/functions defined by you ...
With termsIn09to12 As (
	Select termId, Courses.id As courseId
	From Courses
	Join (
		Select Terms.id As termId
		From Terms
		Where Terms.year Between 2009 And 2012
	) As couresIn
	On couresIn.termId = Courses.term
	Join (
		Select id As courseId
		From Subjects
		Where code = 'COMP3311'
	) As comp3311
	On Courses.subject = comp3311.courseId
), 
failStu As (
	Select count(student) As numFail, course As courseId
	From Course_enrolments
	Where mark < 50
	And mark is not null
	Group By course
),
numFailStu As (
	Select termId, sum(numFail) As fails
	From termsIn09to12
	Join failStu
	On termsIn09to12.courseId = failStu.courseId
	Group By termId
),
stuInTerm As (
	Select count(student) As numStu, course As courseId
	From Course_enrolments
	Where mark is not null
	Group By course
),
numStu As (
	Select termId, sum(numStu) As all
	From termsIn09to12
	Join stuInTerm
	On termsIn09to12.courseId = stuInTerm.courseId
	Group By termId
),
failRate As (
	Select numFailStu.termId, numFailStu.fails/numStu.all As rate
	From numFailStu
	Join numStu
	On numFailStu.termId = numStu.termId
)
Select term, round(rate, 4) As min_fail_rate
From failRate
Join (
	Select Terms.name as term, id
	From Terms
) As termName
On failRate.termId = termName.id
Where rate 
	=
	(Select min(rate)
	From failRate) 
;


-- Q5b
create or replace view Q5b(term, min_fail_rate)
as
--... SQL statements, possibly using other views/functions defined by you ...
With termsIn09to12 As (
	Select termId, Courses.id As courseId
	From Courses
	Join (
		Select Terms.id As termId
		From Terms
		Where Terms.year Between 2016 And 2019
	) As couresIn
	On couresIn.termId = Courses.term
	Join (
		Select id As courseId
		From Subjects
		Where code = 'COMP3311'
	) As comp3311
	On Courses.subject = comp3311.courseId
), 
failStu As (
	Select count(student) As numFail, course As courseId
	From Course_enrolments
	Where mark < 50
	And mark is not null
	Group By course
),
numFailStu As (
	Select termId, sum(numFail) As fails
	From termsIn09to12
	Join failStu
	On termsIn09to12.courseId = failStu.courseId
	Group By termId
),
stuInTerm As (
	Select count(student) As numStu, course As courseId
	From Course_enrolments
	Where mark is not null
	Group By course
),
numStu As (
	Select termId, sum(numStu) As all
	From termsIn09to12
	Join stuInTerm
	On termsIn09to12.courseId = stuInTerm.courseId
	Group By termId
),
failRate As (
	Select numFailStu.termId, numFailStu.fails/numStu.all As rate
	From numFailStu
	Join numStu
	On numFailStu.termId = numStu.termId
)
Select term, round(rate, 4) As min_fail_rate
From failRate
Join (
	Select Terms.name as term, id
	From Terms
) As termName
On failRate.termId = termName.id
Where rate 
	=
	(Select min(rate)
	From failRate) 
;


-- Q6
create or replace function 
	Q6(id integer,code text) returns integer
as $$
--... SQL statements, possibly using other views/functions defined by you ...
With marksOfCourse As (
	Select student, mark
	From Course_enrolments
	Join (
		Select Courses.id As courseId
		From Courses
		Join (--param subject的subject id
			Select Subjects.id As subjectId
			From Subjects
			Where Subjects.code = $2
		) As subjectList
		On Courses.subject = subjectId
	) As c
	On courseId = Course_enrolments.course
)

Select mark
From marksOfCourse
Where $1 = student
$$ language sql;


-- Q7
create or replace function 
	Q7(year integer, session text) returns table (code text)
as $$
--... SQL statements, possibly using other views/functions defined by you ...
With PGcomp As (
	Select *
	From Courses
	Join (
		Select id As courseId, code
		From Subjects
		Where code Like 'COMP%'
		And
		career = 'PG'
	) As PGCompCourse
	On Courses.subject = PGCompCourse.courseId
)

Select code
From PGcomp
Join (
	Select id
	From Terms
	Where year = $1
	And session = $2
) As termCode
On PGcomp.term = termCode.id
$$ language sql;


-- Q8
create or replace function
	Q8(zid integer) returns setof TermTranscriptRecord
as $$
--... SQL statements, possibly using other views/functions defined by you ...
With studentCourses As (
	Select course, mark, grade, termId
	From Course_enrolments
	Join (
		Select id
		From People
		Where unswid = $1
	) As Person
	On Course_enrolments.student = Person.id
	Join (
		Select term As termId, id As courseId
		From Courses
	) As terms
	On Course_enrolments.course = terms.courseId
),
subjectCourse As (
	Select studentCourses.termId As termId, studentCourses.course As courseId, Subjects.UOC As UOC, mark, grade
	From Courses
	Join Subjects
	On Courses.subject = Subjects.id
	Join studentCourses
	On Courses.id = studentCourses.course
),
passedCourses As (
	Select termId, courseId,
		(Case
			When grade = 'SY' Then UOC
			When grade = 'PT' Then UOC
			When grade = 'PC' Then UOC
			When grade = 'PS' Then UOC
			When grade = 'CR' Then UOC
			When grade = 'DN' Then UOC
			When grade = 'HD' Then UOC
			When grade = 'A' Then UOC
			When grade = 'B' Then UOC
			When grade = 'C' Then UOC
			When grade = 'XE' Then UOC
			When grade = 'T' Then UOC
			When grade = 'PE' Then UOC
			When grade = 'RC' Then UOC
			When grade = 'RS' Then UOC
			Else 0
		End) As UOC
	From subjectCourse
),
numPassedUOC As (
	Select Distinct termId, sum(passedCourses.UOC) As termUOCpassed
	From passedCourses
	Join (
		Select UOC, courseId
		From subjectCourse
	) As UOCs
	On passedCourses.courseId = UOCs.courseId
	Group By termId
),
markedUOC As (
	Select termId,
		(Case
			When mark is not null Then mark
			Else 0
		End) As mark, 
		(Case 
			When mark is not null Then UOC
			Else 0
		End) As UOC
	From subjectCourse
),
termWams As (
	Select Distinct termId, 
		(Case
			When sum(markedUOC.UOC) = 0 Then 0
			Else round(sum(markedUOC.mark*markedUOC.UOC)*1.0/sum(markedUOC.UOC), 0)
		End) As termWam
	From markedUOC
	Group By termId
), 
finalT As (
	Select termname(termWams.termId), 
		Case 
			When termWam = 0 Then null
			Else termWam
		End,
		Case
			When termUOCpassed = 0 Then null
			Else termUOCpassed
		End
	From termWams
	Join numPassedUOC
	On termWams.termId = numPassedUOC.termId
),
summaryWam As (
	Select 1 as Id, 
		(Case
			When sum(UOC) = 0 Then null
			Else round(sum(mark*UOC)*1.0/sum(UOC))
		End) As avgWam
	From markedUOC
),
summaryUOC As (
	Select 1 as Id, 
		(Case 
			When sum(termUOCpassed) = 0 Then null
			Else sum(termUOCpassed)
		End) As totalUOC
	From numPassedUOC
)

Select *
From finalT
Union All (
	Select 'OVAL', summaryWam.avgWam, summaryUOC.totalUOC
	From summaryWam
	Join summaryUOC
	On summaryWam.id = summaryUOC.id
	Where 0 <
		(Select count(*)
		From finalT)
)
$$ language sql;

-- Q9
create or replace function 
	Q9(gid integer) returns setof AcObjRecord
as $$
--... SQL statements, possibly using other views/functions defined by you ...
declare
gTable record;
defInRow text;
abr AcObjRecord;
begin
	Select * into gTable
	From Acad_object_groups
	Where Acad_object_groups.id = $1;

	if (not found) then
		raise exception 'No such group %', $1;
	end if;

	if (gTable.gdefBy = 'enumerated') then
		if (gTable.gType = 'stream') then
			For abr in
				Select Acad_object_groups.gtype As objtype, Streams.code As objcode
				From Acad_object_groups
				Join Stream_group_members
				On Stream_group_members.ao_group = Acad_object_groups.id
				Join Streams
				On Stream_group_members.stream = Streams.id
				Where Acad_object_groups.id = $1
			Loop
				return next abr;
			end loop;
		elsif (gTable.gType = 'subject') then
			For abr in
				Select Acad_object_groups.gtype As objtype, Subjects.code As objcode
				From Acad_object_groups
				Join Subject_group_members
				On Subject_group_members.ao_group = Acad_object_groups.id
				Join Subjects
				On Subject_group_members.subject = Subjects.id
				Where Acad_object_groups.id = $1
			Loop
				return next abr;
			end loop;

		elsif (gTable.gType = 'program') then
			For abr in
				Select Acad_object_groups.gtype As objtype, Programs.code As objcode
				From Acad_object_groups
				Join Program_group_members
				On Program_group_members.ao_group = Acad_object_groups.id
				Join Programs
				On Program_group_members.program = Programs.id
				Where Acad_object_groups.id = $1
			Loop
				return next abr;
			end loop;
		end if;
	else
		if (gTable.gType = 'program') then
			For abr in
				Select 'program' As objtype, regexp_split_to_table(gTable.definition, ',') As objcode
			Loop
				return next abr;
			end loop;
		elsif (gTable.gType = 'subject') then
			For abr in
				Select 'subject' As objtype, regexp_split_to_table(gTable.definition, ',') As objcode
			Loop
				return next abr;
			end loop;
		end if;
	end if;

end
$$ language plpgsql;


-- Q10
create or replace function
	Q10(code text) returns setof text
as $$
--... SQL statements, possibly using other views/functions defined by you ...
declare
prereq text;
subjectId integer;
ruleId integer;
aogId integer;
begin
	Select id into subjectId
	From Subjects
	Where Subjects.code = $1;

	Select rule into ruleId
	From Subject_prereqs
	Where subjectId = subject;

	Select ao_group into aogId
	From Rules
	Where ruleId = id;

	For prereq in
		Select Subjects.code
		From Acad_object_groups
		Join Subject_group_members
		On Subject_group_members.ao_group = Acad_object_groups.id
		Join Subjects
		On Subject_group_members.subject = Subjects.id
		Where Acad_object_groups.id = aogId
	Loop
		return next prereq;
	end loop;
end;
$$ language plpgsql;