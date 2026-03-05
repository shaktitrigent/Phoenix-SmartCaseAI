const STEPS = ["Fetch Jira Issue", "Generate Test Cases", "Review Output", "Push to TestRail"];

function StepFlow({ activeStep = 1 }) {
  return (
    <div className="card step-flow-card">
      <div className="step-flow">
        {STEPS.map((step, index) => {
          const stepNumber = index + 1;
          const state = stepNumber < activeStep ? "done" : stepNumber === activeStep ? "active" : "pending";
          return (
            <div key={step} className={`step-item ${state}`}>
              <span className="step-dot">{stepNumber}</span>
              <span className="step-label">{step}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default StepFlow;
