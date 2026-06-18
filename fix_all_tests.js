const fs = require('fs');

const rankMock = `
    await page.route('**/v1/actions/rank', async route => {
      await route.fulfill({ json: { actions: [], total_achievable_reduction: 0 } }).catch(() => {});
    });
`;

function fixTest(file) {
    let content = fs.readFileSync(file, 'utf8');

    if (content.includes('test.beforeEach(async ({ page }) => {')) {
        if (!content.includes('**/v1/actions/rank')) {
            content = content.replace('test.beforeEach(async ({ page }) => {', 'test.beforeEach(async ({ page }) => {' + rankMock);
        }
    } else {
        if (!content.includes('test.beforeEach')) {
            content = content.replace(/test\.describe\('.*?', \(\) => \{/, match => match + '\n  test.beforeEach(async ({ page }) => {' + rankMock + '  });\n');
        }
    }

    fs.writeFileSync(file, content);
}

const files = [
    'frontend/tests/e2e/accessibility.spec.ts',
    'frontend/tests/e2e/ai-parsing.spec.ts',
    'frontend/tests/e2e/simulator.spec.ts',
    'frontend/tests/e2e/ocr-upload.spec.ts',
    'frontend/tests/e2e/manual-entry.spec.ts',
    'frontend/tests/e2e/recommendations.spec.ts'
];

files.forEach(fixTest);
