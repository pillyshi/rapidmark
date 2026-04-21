export default {
  definition: {
    id: 'test_task',
    name: 'Test NER Task',
    type: 'ner',
    description: 'A task definition for testing',
    labels: [
      { id: 'person', name: 'Person', parentId: null },
      { id: 'organization', name: 'Organization', parentId: null },
      { id: 'location', name: 'Location', parentId: null },
    ],
  },
  texts: [
    {
      id: 'text_1',
      content: 'Apple CEO Tim Cook announced the new iPhone at the company headquarters in Cupertino.',
      attributes: { source: 'tech_news' }
    },
    {
      id: 'text_2',
      content: 'Microsoft acquired LinkedIn in 2016 for $26 billion.',
      attributes: { source: 'business_news' }
    },
    {
      id: 'text_3',
      content: 'Google DeepMind researchers published a breakthrough paper on AI.',
      attributes: { source: 'science_news' }
    }
  ]
}
