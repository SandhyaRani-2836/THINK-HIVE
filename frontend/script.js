document.getElementById("projectForm").addEventListener("submit", async function (e) {
  e.preventDefault();

  const formData = {
    student_name: document.getElementById("student_name").value,
    department: document.getElementById("department").value,
    problem_statement: document.getElementById("problem_statement").value,
    drawbacks: document.getElementById("drawbacks").value,
    code: document.getElementById("code").value,
  };

  try {
    const response = await fetch("http://127.0.0.1:5000/submit", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(formData),
    });

    const result = await response.json();
    document.getElementById("statusMessage").textContent = result.message;
  } catch (error) {
    console.error("Error:", error);
    document.getElementById("statusMessage").textContent = "Something went wrong!";
  }
});
