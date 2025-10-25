from fastapi import FastAPI, Body
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from pydantic import BaseModel
from bson import ObjectId

app = FastAPI()

# ===== CORS =====
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== MongoDB =====
client = MongoClient("mongodb://127.0.0.1:27017")
db = client["complaintsDB"]

# ===== Pydantic Models =====
class Register(BaseModel):
    studentName: str
    email: str
    studentId: str
    password: str

class Login(BaseModel):
    email: str
    password: str

class Complaint(BaseModel):
    studentName: str
    studentId: str
    title: str
    category: str
    description: str

# ===== Home Page =====
@app.get("/", response_class=HTMLResponse)
def home_page():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>SCMS Home</title>
<style>
body { font-family: 'Segoe UI', sans-serif; margin:0; padding:0; background:#f0f2f5; }
header { background:#00bfff; color:white; padding:20px; text-align:center; font-size:28px; font-weight:bold; }
section { max-width:600px; margin:30px auto; background:white; padding:25px; border-radius:12px; box-shadow:0 5px 20px rgba(0,0,0,0.1); }
h2 { margin-top:0; color:#333; }
input, select, textarea { width:100%; padding:12px; margin:8px 0 18px 0; border:1px solid #ccc; border-radius:8px; font-size:16px; }
button { background:#00bfff; color:white; border:none; padding:12px 25px; cursor:pointer; border-radius:8px; font-size:16px; transition:0.3s; }
button:hover { background:#009acd; }
p { text-align:center; }
a { cursor:pointer; color:#00bfff; text-decoration:none; }
a:hover { text-decoration:underline; }
#adminLoginBtn { display:block; margin:15px auto; background:#ff7f50; }
</style>
</head>
<body>

<header>Student Complaint Management System</header>

<section id="registerSection">
    <h2>Register</h2>
    <form id="registerForm">
        <input type="text" id="studentName" placeholder="Full Name" required>
        <input type="email" id="email" placeholder="Email" required>
        <input type="text" id="studentId" placeholder="Student ID" required>
        <input type="password" id="password" placeholder="Password" required>
        <input type="password" id="confirmPassword" placeholder="Confirm Password" required>
        <button type="submit">Register</button>
    </form>
    <p>Already have an account? <a id="showLogin">Login here</a></p>
</section>

<section id="loginSection" style="display:none;">
    <h2>Login</h2>
    <form id="loginForm">
        <input type="email" id="loginEmail" placeholder="Email" required>
        <input type="password" id="loginPassword" placeholder="Password" required>
        <button type="submit">Login</button>
    </form>
    <p>No account? <a id="showRegister">Register here</a></p>
</section>

<button id="adminLoginBtn">Admin Login</button>

<script>
const API_BASE = "http://127.0.0.1:5500";

// Toggle sections
document.getElementById("showLogin").addEventListener("click", ()=>{document.getElementById("registerSection").style.display="none"; document.getElementById("loginSection").style.display="block";});
document.getElementById("showRegister").addEventListener("click", ()=>{document.getElementById("loginSection").style.display="none"; document.getElementById("registerSection").style.display="block";});

// Admin login
document.getElementById("adminLoginBtn").addEventListener("click", ()=>{const pwd=prompt("Enter Admin Password:"); if(pwd==="Admin@123"){window.location.href="/admin";}else{alert("❌ Incorrect password!")}});

// Register
document.getElementById("registerForm").addEventListener("submit", async (e)=>{
    e.preventDefault();
    const studentName=document.getElementById("studentName").value.trim();
    const email=document.getElementById("email").value.trim();
    const studentId=document.getElementById("studentId").value.trim();
    const password=document.getElementById("password").value.trim();
    const confirmPassword=document.getElementById("confirmPassword").value.trim();
    if(password!==confirmPassword){ alert("Passwords do not match!"); return; }
    try{
        const res=await fetch(API_BASE+"/register",{method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({studentName,email,studentId,password})});
        const data=await res.json();
        if(data.success){ alert("Registered! Login below."); document.getElementById("registerSection").style.display="none"; document.getElementById("loginSection").style.display="block";}
        else alert(data.message||"Registration failed!");
    }catch(err){console.error(err); alert("Server error!");}
});

// Login
document.getElementById("loginForm").addEventListener("submit", async (e)=>{
    e.preventDefault();
    const email=document.getElementById("loginEmail").value.trim();
    const password=document.getElementById("loginPassword").value.trim();
    try{
        const res=await fetch(API_BASE+"/login",{method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({email,password})});
        const data=await res.json();
        if(data.success){
            localStorage.setItem("studentName", data.studentName);
            localStorage.setItem("studentId", data.studentId);
            window.location.href="/student";
        } else alert("Invalid Email or Password!");
    }catch(err){console.error(err); alert("Server error!");}
});
</script>

</body>
</html>
"""

# ===== Student Dashboard =====
@app.get("/student", response_class=HTMLResponse)
def student_dashboard():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Student Dashboard</title>
<style>
body { font-family:'Segoe UI',sans-serif; margin:0; padding:0; height:100vh;
background:linear-gradient(-45deg,violet,indigo,blue,green,teal,purple,pink);
background-size:800% 800%; animation:vibgyorBG 30s ease-in-out infinite; overflow-x:hidden; }
body::before { content:""; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(255,255,255,0.02); pointer-events:none; }
@keyframes vibgyorBG { 0%{background-position:0% 50%} 25%{background-position:50% 100%} 50%{background-position:100% 50%} 75%{background-position:50% 0%} 100%{background-position:0% 50%} }
header { background:rgba(255,255,255,0.15); color:white; padding:20px; text-align:center; font-size:24px; font-weight:bold; text-shadow:1px 1px 5px #000; }
section { max-width:700px; margin:20px auto; background:rgba(255,255,255,0.9); padding:25px; border-radius:12px; box-shadow:0 5px 20px rgba(0,0,0,0.1); }
input, select, textarea { width:100%; padding:12px; margin:8px 0 18px 0; border:1px solid #ccc; border-radius:8px; font-size:16px; }
button { background:#00bfff; color:white; border:none; padding:12px 25px; cursor:pointer; border-radius:8px; font-size:16px; transition:0.3s; }
button:hover { background:#009acd; }
table { width:100%; border-collapse:collapse; margin-top:15px; }
table, th, td { border:1px solid #ddd; }
th, td { padding:12px; text-align:left; }
tr:nth-child(even){background:#f9f9f9;}
#toast{display:none; position:fixed; bottom:20px; left:50%; transform:translateX(-50%); background:#333; color:white; padding:10px 20px; border-radius:8px; opacity:0.9;}
</style>
</head>
<body>
<header>Student Dashboard</header>
<section>
<p>Welcome, <span id="userName"></span> | <button id="logoutBtn">Logout</button></p>
<h3>Submit Complaint</h3>
<form id="complaintForm">
<input type="text" id="title" placeholder="Complaint Title" required>
<select id="category">
<option value="">Select Category</option>
<option value="Academic">Academic</option>
<option value="Hostel">Hostel</option>
<option value="Library">Library</option>
<option value="Infrastructure">Infrastructure</option>
<option value="Transport">Transport</option>
<option value="Canteen">Canteen</option>
<option value="Administration">Administration</option>
<option value="Other">Other</option>
</select>
<textarea id="description" placeholder="Complaint Description" rows="4" required></textarea>
<button type="submit">Submit Complaint</button>
</form>
<h3>Your Complaints</h3>
<table id="complaintsTable">
<tr><th>#</th><th>Title</th><th>Category</th><th>Description</th><th>Status</th></tr>
</table>
</section>
<div id="toast"></div>
<script>
const API_BASE="http://127.0.0.1:5500";

const studentName=localStorage.getItem("studentName");
const studentId=localStorage.getItem("studentId");
document.getElementById("userName").innerText=studentName;

document.getElementById("logoutBtn").addEventListener("click",()=>{localStorage.clear(); window.location.href="/";});

// Submit complaint
document.getElementById("complaintForm").addEventListener("submit", async (e)=>{
e.preventDefault();
const title=document.getElementById("title").value.trim();
const category=document.getElementById("category").value;
const description=document.getElementById("description").value.trim();
if(!title||!category||!description){ showToast("⚠️ Fill all fields!"); return; }
try{
const res=await fetch(API_BASE+"/complaints",{method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({studentName,studentId,title,category,description})});
const data=await res.json();
if(data.success){ document.getElementById("complaintForm").reset(); showToast("✅ Complaint submitted!"); loadComplaints(); }
else showToast("❌ Failed to submit complaint!");
}catch(err){console.error(err); showToast("Server error!");}
});

// Load complaints
async function loadComplaints(){
const table=document.getElementById("complaintsTable");
try{
const res=await fetch(`${API_BASE}/complaints/${studentId}`);
const complaints=await res.json();
let rows="<tr><th>#</th><th>Title</th><th>Category</th><th>Description</th><th>Status</th></tr>";
complaints.forEach((c,i)=>{ rows+=`<tr><td>${i+1}</td><td>${c.title}</td><td>${c.category}</td><td>${c.description}</td><td>${c.status||"Pending"}</td></tr>`; });
table.innerHTML=rows;
}catch(err){console.error(err); table.innerHTML="<tr><td colspan='5'>Failed to load complaints</td></tr>";}
}

function showToast(msg){const t=document.getElementById("toast"); t.innerText=msg; t.style.display="block"; setTimeout(()=>t.style.display="none",3000);}
loadComplaints();
</script>
</body>
</html>
"""

# ===== Admin Dashboard =====
@app.get("/admin", response_class=HTMLResponse)
def admin_dashboard():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Admin Dashboard</title>
<style>
body { font-family: 'Segoe UI', sans-serif; margin:0; padding:0; background:#f0f2f5; }
header { background:#ff7f50; color:white; padding:20px; text-align:center; font-size:24px; font-weight:bold; }
section { max-width:1000px; margin:20px auto; background:white; padding:25px; border-radius:12px; box-shadow:0 5px 20px rgba(0,0,0,0.1); }
input, select { padding:10px; margin:5px; border-radius:6px; border:1px solid #ccc; }
button { background:#ff7f50; color:white; border:none; padding:10px 20px; border-radius:6px; cursor:pointer; transition:0.3s; }
button:hover { background:#e66b3c; }
table { width:100%; border-collapse:collapse; margin-top:15px; }
th, td { border:1px solid #ddd; padding:10px; text-align:left; }
tr:nth-child(even) { background:#f9f9f9; }
.delete { background:#dc3545; margin-left:5px; }
.delete:hover { background:#b52a37; }
</style>
</head>
<body>
<header>Admin Dashboard</header>
<section>
<h3>All Complaints</h3>
<div class="filters">
<input type="text" id="filterStudent" placeholder="Filter by Student Name">
<select id="filterCategory"><option value="">All Categories</option><option value="Academic">Academic</option><option value="Hostel">Hostel</option><option value="Library">Library</option><option value="Infrastructure">Infrastructure</option><option value="Transport">Transport</option><option value="Canteen">Canteen</option><option value="Administration">Administration</option><option value="Other">Other</option></select>
<select id="filterStatus"><option value="">All Status</option><option value="Pending">Pending</option><option value="Resolved">Resolved</option></select>
<button id="applyFilters">Apply Filters</button>
<button id="resetFilters">Reset</button>
</div>
<table id="adminComplaintsTable">
<tr><th>#</th><th>Student Name</th><th>Student ID</th><th>Title</th><th>Category</th><th>Description</th><th>Status</th><th>Action</th></tr>
</table>
</section>
<script>
const API_BASE="http://127.0.0.1:5500";

async function loadAdminComplaints(){
const table=document.getElementById("adminComplaintsTable");
try{
let res=await fetch(`${API_BASE}/complaints`);
let complaints=await res.json();
const studentFilter=document.getElementById("filterStudent").value.trim().toLowerCase();
const categoryFilter=document.getElementById("filterCategory").value;
const statusFilter=document.getElementById("filterStatus").value;
if(studentFilter) complaints=complaints.filter(c=>c.studentName.toLowerCase().includes(studentFilter));
if(categoryFilter) complaints=complaints.filter(c=>c.category===categoryFilter);
if(statusFilter) complaints=complaints.filter(c=>(c.status||"Pending")===statusFilter);
let rows="<tr><th>#</th><th>Student Name</th><th>Student ID</th><th>Title</th><th>Category</th><th>Description</th><th>Status</th><th>Action</th></tr>";
complaints.forEach((c,i)=>{
const status=c.status||"Pending";
rows+=`<tr><td>${i+1}</td><td>${c.studentName}</td><td>${c.studentId}</td><td>${c.title}</td><td>${c.category}</td><td>${c.description}</td><td>${status}</td><td><button class="${status==='Resolved'?'pending':'resolve'}" onclick="toggleStatus('${c.studentId}','${c.title}','${status}')">${status==='Resolved'?'Mark Pending':'Mark Resolved'}</button>${status==='Resolved'?` <button class="delete" onclick="deleteComplaint('${c.studentId}','${c.title}')">Delete</button>` : ''}</td></tr>`;
});
table.innerHTML=rows;
}catch(err){ console.error(err); }
}

async function toggleStatus(studentId,title,currentStatus){
const newStatus=currentStatus==="Resolved"?"Pending":"Resolved";
try{
const res=await fetch(`${API_BASE}/complaints/update`,{method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({studentId,title,status:newStatus})});
const data=await res.json(); if(data.success) loadAdminComplaints();
}catch(err){console.error(err);}
}

async function deleteComplaint(studentId,title){
if(!confirm("Are you sure you want to delete this resolved complaint?")) return;
try{
const res=await fetch(`${API_BASE}/complaints/delete`,{method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({studentId,title})});
const data=await res.json(); if(data.success){ alert("🗑️ Complaint deleted"); loadAdminComplaints(); } else alert(data.message||"❌ Failed to delete complaint");
}catch(err){console.error(err); alert("Server error!");}
}

document.getElementById("applyFilters").addEventListener("click",loadAdminComplaints);
document.getElementById("resetFilters").addEventListener("click",()=>{document.getElementById("filterStudent").value=""; document.getElementById("filterCategory").value=""; document.getElementById("filterStatus").value=""; loadAdminComplaints();});
loadAdminComplaints();
</script>
</body>
</html>
"""

# ===== API Routes =====

# Register student
@app.post("/register")
def register_student(data: Register):
    if db.students.find_one({"studentId": data.studentId}):
        return {"success": False, "message": "Student ID already exists!"}
    if db.students.find_one({"email": data.email}):
        return {"success": False, "message": "Email already registered!"}
    db.students.insert_one(data.dict())
    return {"success": True}

# Login student
@app.post("/login")
def login_student(data: Login):
    user = db.students.find_one({"email": data.email, "password": data.password}, {"_id":0})
    if user:
        return {"success": True, "studentName": user["studentName"], "studentId": user["studentId"]}
    return {"success": False}

# Add complaint
@app.post("/complaints")
def add_complaint(data: Complaint):
    db.complaints.insert_one(data.dict())
    return {"success": True}

# Get student complaints
@app.get("/complaints/{studentId}")
def get_student_complaints(studentId: str):
    complaints=list(db.complaints.find({"studentId": studentId}, {"_id":0}))
    return complaints

# Get all complaints (admin)
@app.get("/complaints")
def get_all_complaints():
    complaints=list(db.complaints.find({}, {"_id":0}))
    return complaints

# Update complaint status (admin)
@app.post("/complaints/update")
def update_complaint_status(data: dict = Body(...)):
    studentId=data["studentId"]
    title=data["title"]
    status=data["status"]
    result=db.complaints.update_one({"studentId":studentId,"title":title},{"$set":{"status":status}})
    if result.modified_count>0: return {"success":True}
    return {"success":False,"message":"Update failed"}

# Delete complaint (admin)
@app.post("/complaints/delete")
def delete_complaint(data: dict = Body(...)):
    studentId=data["studentId"]
    title=data["title"]
    result=db.complaints.delete_one({"studentId":studentId,"title":title,"status":"Resolved"})
    if result.deleted_count>0: return {"success":True}
    return {"success":False,"message":"Delete failed"}
