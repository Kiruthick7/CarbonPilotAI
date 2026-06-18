const fs = require('fs');

const rankMock = `
    await page.route('http://127.0.0.1:8000/v1/actions/rank', async route => {
      await route.fulfill({ json: { actions: [], total_achievable_reduction: 0 } });
    });
`;

const calcMock = `
    await page.route('http://127.0.0.1:8000/v1/calculate', async route => {
      await route.fulfill({ json: { inventory: { total_tco2e: 7.88, breakdowns: [{ category: "digital", total_kgco2e: 160 }] } } });
    });
`;

const processAndContinueRe = /await page\.click\('button:has-text\("Process & Continue"\)'\);/;
const finishAndDashboardStr = `
    await page.click('button:has-text("Process & Continue")');
    await page.click('button:has-text("Finish & View Dashboard")');
`;

const processManualRe = /await page\.click\('button:has-text\("Generate Carbon Profile"\)'\);/;
const finishManualStr = `
    await page.click('button:has-text("Generate Carbon Profile")');
    await page.click('button:has-text("Finish & View Dashboard")');
`;

function fixTest(file, type) {
    let content = fs.readFileSync(file, 'utf8');
    if (!content.includes('/actions/rank')) {
        content = content.replace(/test\('.*?', async \(\{ page \}\) => \{/, match => match + '\n' + rankMock + '\n' + calcMock);
    }
    
    if (type === 'ocr') {
        content = content.replace(processAndContinueRe, finishAndDashboardStr);
    } else if (type === 'manual') {
        content = content.replace(processManualRe, finishManualStr);
        // Also add manual mock if missing
        if (!content.includes('/ocr/manual')) {
            const manualMock = `
    await page.route('http://127.0.0.1:8000/v1/ocr/manual', async route => {
      await route.fulfill({ json: { success: true, profile: {}, inventory: { total_tco2e: 7.72, breakdowns: [] } } });
    });
`;
            content = content.replace(/test\('.*?', async \(\{ page \}\) => \{/, match => match + '\n' + manualMock);
        }
    }
    fs.writeFileSync(file, content);
}

fixTest('frontend/tests/e2e/ocr-upload.spec.ts', 'ocr');
fixTest('frontend/tests/e2e/manual-entry.spec.ts', 'manual');

