---
title: "Your agent answers from the URL you typed when you created it, in every topic"
summary: "Generative answers answers when no topic matches, and agent-level knowledge is used in every feature, so a scoped topic can still be answered from somewhere else."
surface: power-platform
tip_number: 30
state: draft
source: "https://learn.microsoft.com/en-us/microsoft-copilot-studio/nlu-boost-node"
next_step: "In a trial agent, ask a question that matches no topic and record which knowledge source answered, then add a topic-level source and ask the same question again."
---

**Tip**

Know which of the two knowledge paths answered before you tune either one. The documented model has
a fallback in the middle of it:

> When you first create your agent, you can enter a URL your agent uses to generate responses. The
> agent uses this URL in all features. However, you can enhance your agent's conversations by using
> multiple internal and external knowledge sources within individual topics.

and then the part that surprises people:

> Generative answers as a fallback: When your agent can't find a matching intent (defined in a topic)
> for the user's query, it uses generative answers to try to answer the question.

So there are two ways a question gets answered: a topic you wrote, or generative answers reaching for
knowledge. When the answer is wrong, the question to ask is not "is my topic wrong" but "did my topic
even run" - the answer may have come from the fallback path using knowledge you forgot you attached.

If the user's intent matches neither a topic nor generative answers, the Fallback system topic takes
over, which is where escalation lives.

**Try it**

Ask your agent something no topic covers and watch the test pane. That is the fallback path, and it
is answering with everything you have configured.
