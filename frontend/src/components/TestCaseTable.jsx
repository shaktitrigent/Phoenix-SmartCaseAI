function TestCaseTable({ testCases }) {
  if (!testCases?.length) {
    return (
      <div className="panel">
        <h3>Test Cases</h3>
        <p>No test cases generated yet.</p>
      </div>
    );
  }

  return (
    <div className="panel">
      <h3>Generated Test Cases ({testCases.length})</h3>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Title</th>
              <th>Preconditions</th>
              <th>Steps</th>
              <th>Expected Result</th>
              <th>Type</th>
              <th>Priority</th>
            </tr>
          </thead>
          <tbody>
            {testCases.map((item) => (
              <tr key={item.test_case_id || item.title}>
                <td>{item.test_case_id}</td>
                <td>{item.title}</td>
                <td>{item.preconditions}</td>
                <td>
                  <ol>
                    {(item.steps || []).map((s, idx) => (
                      <li key={`${item.test_case_id}-${idx}`}>{s}</li>
                    ))}
                  </ol>
                </td>
                <td>{item.expected_result}</td>
                <td>{item.test_type}</td>
                <td>{item.priority}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default TestCaseTable;

