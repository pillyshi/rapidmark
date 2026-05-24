export default {
  definition: {
    id: 'cls_task',
    name: 'Sentiment',
    type: 'classification',
    description: 'A classification task for testing',
    labels: [
      { id: 'pos', name: 'Positive', parentId: null },
      { id: 'neg', name: 'Negative', parentId: null },
    ],
  },
  texts: [
    { id: 'text_1', content: 'Great product!' },
    { id: 'text_2', content: 'Terrible experience.' },
  ],
}
