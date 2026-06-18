const fs = require('fs');

function replaceFile(file, search, replace) {
  let content = fs.readFileSync(file, 'utf8');
  content = content.split(search).join(replace);
  fs.writeFileSync(file, content);
}

// 1. simulator/page.tsx
replaceFile('frontend/src/app/(main)/simulator/page.tsx', 'import { useEffect, useState }', 'import { useState }');
replaceFile('frontend/src/app/(main)/simulator/page.tsx', 
  '"What if I switch to a vegan diet and install solar panels?"', 
  '&quot;What if I switch to a vegan diet and install solar panels?&quot;');
replaceFile('frontend/src/app/(main)/simulator/page.tsx', 
  'as any[]', 
  'as Array<{category: string; total_kgco2e: number}>');

// 2. actions/page.tsx
replaceFile('frontend/src/app/(main)/actions/page.tsx', 'import { useEffect }', '');
replaceFile('frontend/src/app/(main)/actions/page.tsx', 'import { useState, useEffect }', 'import { useState }');
replaceFile('frontend/src/app/(main)/actions/page.tsx', 'import React, { useEffect }', 'import React');
// Let's do regex for actions
let actionsCode = fs.readFileSync('frontend/src/app/(main)/actions/page.tsx', 'utf8');
actionsCode = actionsCode.replace(/import\s*\{\s*useEffect\s*\}\s*from\s*['"]react['"];?/g, '');
actionsCode = actionsCode.replace(/,\s*useEffect/g, '');
fs.writeFileSync('frontend/src/app/(main)/actions/page.tsx', actionsCode);

// 3. dashboard/page.tsx
let dashboardCode = fs.readFileSync('frontend/src/app/(main)/dashboard/page.tsx', 'utf8');
dashboardCode = dashboardCode.replace(/import\s*\{\s*useState,\s*useEffect\s*\}\s*from\s*['"]react['"];?/g, '');
dashboardCode = dashboardCode.replace(/import\s*\{\s*useEffect,\s*useState\s*\}\s*from\s*['"]react['"];?/g, '');
fs.writeFileSync('frontend/src/app/(main)/dashboard/page.tsx', dashboardCode);

// 4. layout.tsx
let layoutCode = fs.readFileSync('frontend/src/app/(main)/layout.tsx', 'utf8');
layoutCode = layoutCode.replace(/<img src="\/logo.png"/g, '<Image src="/logo.png" unoptimized width={36} height={36}');
if (!layoutCode.includes('import Image')) {
  layoutCode = 'import Image from "next/image";\n' + layoutCode;
}
fs.writeFileSync('frontend/src/app/(main)/layout.tsx', layoutCode);

// 5. page.tsx
let homeCode = fs.readFileSync('frontend/src/app/page.tsx', 'utf8');
homeCode = homeCode.replace(/<img src="\/logo.png"/g, '<Image src="/logo.png" unoptimized width={48} height={48}');
if (!homeCode.includes('import Image')) {
  homeCode = 'import Image from "next/image";\n' + homeCode;
}
fs.writeFileSync('frontend/src/app/page.tsx', homeCode);

// 6. onboarding/page.tsx
replaceFile('frontend/src/app/onboarding/page.tsx', 'as any', 'as unknown');

// 7. TrustModal.tsx
let modalCode = fs.readFileSync('frontend/src/components/TrustModal.tsx', 'utf8');
modalCode = modalCode.replace(/import\s*\{\s*useState\s*\}\s*from\s*['"]react['"];?/g, '');
modalCode = modalCode.replace(/,\s*useState/g, '');
fs.writeFileSync('frontend/src/components/TrustModal.tsx', modalCode);

// 8. CarbonDataContext.tsx
let ctxCode = fs.readFileSync('frontend/src/context/CarbonDataContext.tsx', 'utf8');
ctxCode = ctxCode.replace(/\[key: string\]: any;/g, '[key: string]: unknown;');
ctxCode = ctxCode.replace(/Record<string, any>/g, 'Record<string, unknown>');
ctxCode = ctxCode.replace(/setOcrDataState\(JSON\.parse\(dataStr\)\);/, '// eslint-disable-next-line react-hooks/set-state-in-effect\n        setOcrDataState(JSON.parse(dataStr));');
fs.writeFileSync('frontend/src/context/CarbonDataContext.tsx', ctxCode);

console.log("Done");
