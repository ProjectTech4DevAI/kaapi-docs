import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

const sidebars: SidebarsConfig = {
  tutorialSidebar: [
    {type: 'doc', id: 'docs', label: 'Kaapi Overview'},
    {type: 'doc', id: 'architecture', label: 'How Kaapi Works'},
    {type: 'doc', id: 'core-use-cases', label: 'Core Use Cases'},
    {type: 'doc', id: 'getting-started', label: 'Getting Started'},
    {
      type: 'category',
      label: 'Guardrails',
      items: [
        {type: 'doc', id: 'guardrails/content-safety', label: 'Content Safety'},
        {type: 'doc', id: 'guardrails/privacy-protection', label: 'Privacy Protection'},
        {type: 'doc', id: 'guardrails/scope-control', label: 'Scope Control'},
        {type: 'doc', id: 'guardrails/gender-neutrality', label: 'Gender Neutrality'},
      ],
    },
  ],
};

export default sidebars;
