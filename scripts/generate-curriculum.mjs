import fs from "fs";
import path from "path";

const solvedDir = "/home/abhay/code/neetcode-submissions/Data Structures & Algorithms";
const slugs = fs.readdirSync(solvedDir).filter(f => fs.statSync(path.join(solvedDir, f)).isDirectory()).sort();

const patternHeuristics = [
  { pattern: "binary-search", keywords: ["binary-search", "search-insert", "search-2d", "sqrtx", "arranging-coins", "guess-number", "valid-perfect-square", "eating-bananas", "find-k-closest"] },
  { pattern: "stack", keywords: ["daily-temperatures", "evaluate-reverse", "largest-rectangle", "minimum-stack", "validate-parentheses", "valid-parentheses", "crawler-log", "baseball-game", "next-greater"] },
  { pattern: "two-pointers", keywords: ["two-integer-sum-ii", "max-water-container", "three-integer-sum", "is-palindrome", "valid-palindrome", "move-zeroes", "reverse-string", "merge-strings", "remove-duplicates"] },
  { pattern: "sliding-window", keywords: ["buy-and-sell-crypto", "longest-consecutive", "subarray-sum", "count-vowel", "maximum-ascending", "max-consecutive-ones"] },
  { pattern: "trees", keywords: ["depth-of-binary-tree", "invert-a-binary-tree", "valid-sudoku"] },
  { pattern: "heap", keywords: ["last-stone-weight", "take-gifts", "lru-cache", "find-k-closest", "top-k-elements"] },
  { pattern: "linked-list", keywords: [] },
  { pattern: "graphs", keywords: [] },
  { pattern: "greedy", keywords: ["assign-cookies", "lemonade-change", "can-place-flowers", "buy-two-chocolates", "minimum-number-of-moves", "height-checker", "number-of-senior"] },
  { pattern: "intervals", keywords: ["meeting-schedule", "car-fleet", "merge-sorted-array", "interval"] },
  { pattern: "dp-1d", keywords: ["pascals-triangle", "climbing", "house-robber"] },
  { pattern: "dp-2d", keywords: ["range-sum-query-2d"] },
  { pattern: "bit-manipulation", keywords: ["single-number", "missing-number", "sign-of-the-product", "number-of-good-pairs"] },
  { pattern: "tries", keywords: ["counting-words-with-a-given-prefix", "count-prefix-and-suffix", "longest-common-prefix", "string-encode-and-decode"] },
  { pattern: "backtracking", keywords: ["permutation", "combination", "subsets"] },
];

const difficultyMap = {
  "trapping-rain-water": "hard",
  "largest-rectangle-in-histogram": "hard",
  "lru-cache": "medium",
  "valid-sudoku": "medium",
  "car-fleet": "medium",
  "daily-temperatures": "medium",
  "evaluate-reverse-polish-notation": "medium",
  "products-of-array-discluding-self": "medium",
  "longest-consecutive-sequence": "medium",
  "string-encode-and-decode": "medium",
  "three-integer-sum": "medium",
  "max-water-container": "medium",
  "subarray-sum-equals-k": "medium",
  "top-k-elements-in-list": "medium",
  "anagram-groups": "medium",
  "search-2d-matrix": "medium",
  "find-k-closest-elements": "medium",
  "eating-bananas": "medium",
};

const allPatterns = JSON.parse(fs.readFileSync("data/patternOrder.json", "utf8"));

function assignPattern(slug) {
  for (const h of patternHeuristics) {
    if (h.keywords.some(k => slug.includes(k))) return h.pattern;
  }
  // default to arrays-hashing for most
  return "arrays-hashing";
}

function toTitle(slug) {
  return slug.split("-").map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(" ");
}

const slugToNeet = {
  "two-integer-sum": "two-sum",
  "two-integer-sum-ii": "two-sum-ii",
  "three-integer-sum": "three-sum",
  "buy-and-sell-crypto": "best-time-to-buy-and-sell-stock",
  "duplicate-integer": "duplicate-integer",
  "products-of-array-discluding-self": "products-of-array-except-self",
  "top-k-elements-in-list": "top-k-frequent-elements",
  "is-palindrome": "valid-palindrome",
  "valid-palindrome-ii": "valid-palindrome-ii",
  "is-anagram": "valid-anagram",
  "anagram-groups": "group-anagrams",
  "search-2d-matrix": "search-2d-matrix",
  "invert-a-binary-tree": "invert-binary-tree",
  "depth-of-binary-tree": "maximum-depth-of-binary-tree",
  "validate-parentheses": "valid-parentheses",
  "largest-rectangle-in-histogram": "largest-rectangle-in-histogram",
  "trapping-rain-water": "trapping-rain-water",
  "eating-bananas": "koko-eating-bananas",
};

const curriculum = slugs.map(slug => {
  const pattern = assignPattern(slug);
  const diff = difficultyMap[slug] || (slug.includes("easy") ? "easy" : slug.includes("hard") ? "hard" : (Math.random() < 0.5 ? "easy" : Math.random() < 0.7 ? "medium" : "hard"));
  // deterministic pseudo-random based on slug hash
  let hash = 0; for (let i=0;i<slug.length;i++) hash = (hash*31 + slug.charCodeAt(i)) % 100;
  let difficulty;
  if (difficultyMap[slug]) difficulty = difficultyMap[slug];
  else if (hash < 50) difficulty = "easy";
  else if (hash < 85) difficulty = "medium";
  else difficulty = "hard";

  const neetSlug = slugToNeet[slug] || slug;
  return {
    slug,
    name: toTitle(slug),
    pattern,
    difficulty,
    neetcodeUrl: `https://neetcode.io/problems/${neetSlug}`
  };
});

// Add some unsolved placeholders to demonstrate  X / TOTAL and play button fallbacks
const placeholders = [
  { slug: "two-sum-iv", name: "Two Sum IV", pattern: "trees", difficulty: "medium", neetcodeUrl: "https://neetcode.io/problems/two-sum-iv" },
  { slug: "clone-graph", name: "Clone Graph", pattern: "graphs", difficulty: "medium", neetcodeUrl: "https://neetcode.io/problems/clone-graph" },
  { slug: "course-schedule", name: "Course Schedule", pattern: "graphs", difficulty: "medium", neetcodeUrl: "https://neetcode.io/problems/course-schedule" },
  { slug: "house-robber", name: "House Robber", pattern: "dp-1d", difficulty: "medium", neetcodeUrl: "https://neetcode.io/problems/house-robber" },
  { slug: "coin-change", name: "Coin Change", pattern: "dp-1d", difficulty: "medium", neetcodeUrl: "https://neetcode.io/problems/coin-change" },
  { slug: "word-break", name: "Word Break", pattern: "dp-1d", difficulty: "medium", neetcodeUrl: "https://neetcode.io/problems/word-break" },
  { slug: "unique-paths", name: "Unique Paths", pattern: "dp-2d", difficulty: "medium", neetcodeUrl: "https://neetcode.io/problems/unique-paths" },
  { slug: "longest-common-subsequence", name: "Longest Common Subsequence", pattern: "dp-2d", difficulty: "medium", neetcodeUrl: "https://neetcode.io/problems/longest-common-subsequence" },
  { slug: "implement-trie", name: "Implement Trie", pattern: "tries", difficulty: "medium", neetcodeUrl: "https://neetcode.io/problems/implement-trie" },
  { slug: "design-add-and-search-words", name: "Design Add And Search Words", pattern: "tries", difficulty: "medium", neetcodeUrl: "https://neetcode.io/problems/design-add-and-search-words" },
];

const full = [...curriculum, ...placeholders];
full.sort((a,b) => {
  const pa = allPatterns.indexOf(a.pattern);
  const pb = allPatterns.indexOf(b.pattern);
  if (pa !== pb) return pa - pb;
  if (a.difficulty !== b.difficulty) {
    const order = { easy:0, medium:1, hard:2 };
    return order[a.difficulty] - order[b.difficulty];
  }
  return a.slug.localeCompare(b.slug);
});

fs.writeFileSync("data/curriculum.json", JSON.stringify(full, null, 2));
console.log(`Generated ${full.length} entries (${slugs.length} solved + ${placeholders.length} unsolved placeholders)`);
