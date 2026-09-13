# Re-scraping the getcracked progress tree

The tree at `https://getcracked.io/progress-tree/beginner-cpp` is a React Flow graph. Clicking a node opens a side panel whose rows are `<tr>` elements with a link, difficulty cells, and lucide status icons (`lucide-check` correct, `lucide-x` missed, neither means not attempted). Run this in the page (Playwright MCP `browser_evaluate`, logged in) in slices of about 45 nodes, then concatenate the arrays into `gc_tree_items.json` and run `python3 cpp/tools/gc_links.py`.

```js
() => new Promise(async r => {
  const sleep = ms => new Promise(x => setTimeout(x, ms));
  const nodes = [...document.querySelectorAll('.react-flow__node')].filter(n => /^node-/.test(n.dataset.id));
  const out = [];
  for (const n of nodes.slice(0, 45)) {            // then 45..90, then 90..
    n.dispatchEvent(new MouseEvent('click', {bubbles: true}));
    await sleep(700);
    const rows = [...document.querySelectorAll('tr')].filter(tr => tr.querySelector('a[href]')).map(tr => {
      const a = tr.querySelector('a[href]');
      return {href: a.getAttribute('href'), title: a.textContent.trim(),
              cells: [...tr.querySelectorAll('td')].map(td => td.textContent.trim()).slice(0, 4),
              svgs: [...tr.querySelectorAll('svg')].map(s => s.getAttribute('class') || '').join(' ')};
    });
    out.push({id: n.dataset.id, title: n.textContent.trim().replace(/\s+/g, ' '), items: rows});
  }
  r(JSON.stringify(out));
})
```
