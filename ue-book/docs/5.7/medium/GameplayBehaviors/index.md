# AI Behaviors (GameplayBehaviors)

> Encapsulated fire-and-forget behaviors for AI agents

| 属性 | 值 |
|---|---|
| 中文名 | AI行为 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `GameplayBehaviorsModule` (Runtime, UncookedOnly), `GameplayBehaviorsEditorModule` (Editor), `GameplayBehaviorsTestSuite` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-09-27 |
| 年龄标签 | 🆕（约1年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/GameplayBehaviors) | |

## 总体用途

该插件提供一种**“发射后不理”式（fire-and-forget）行为**封装，专为 AI 代理设计。其核心思想是将一次性的、无需持续追踪的复杂行为（如闪避、抛射物攻击、简单导航）打包为独立对象，通过 `GameplayAbilities` 系统执行，从而简化 AI 逻辑的状态管理。

- 解决频繁在行为树中编写大量自定义任务节点的问题。
- 降低 AI 行为与 GameplayAbility 之间的粘合代码量。
- 允许将行为设计为可组合、可复用的模块，与 Lyra 等框架中的 AI 集成方案配合良好。

## 模块列表

| 模块 | 类型 | 一句话说明 |
|---|---|---|
| [GameplayBehaviorsModule.md](GameplayBehaviorsModule.md) | Runtime / UncookedOnly | 提供核心行为基类、数据资产与执行逻辑，实现“发射后不理”行为的创建、触发与生命周期管理 |
| [GameplayBehaviorsEditorModule.md](GameplayBehaviorsEditorModule.md) | Editor | 提供自定义蓝图节点、细节面板定制与编辑器工具，提升行为配置与调试体验 |
| [GameplayBehaviorsTestSuite.md](GameplayBehaviorsTestSuite.md) | Runtime | 包含功能测试与压力测试，验证行为执行、数据绑定与多代理并发场景的正确性 |

## 使用场景

- **AI 闪避 / 翻滚**：当 AI 受到攻击时触发一个 `UGameplayBehavior_Attack` 子类，行为执行期间角色无敌、播放动画、移动至安全位置，无需行为树节点持续轮询。
- **一次性弹幕攻击**：AI 在某个时机生成大量抛射物，行为结束后自动清理，无需手动管理状态机。
- **与 Gameplay Abilities 深度集成**：利用 `GameplayEffect`、`GameplayTag` 等机制控制行为的启动、打断与冷却，兼容现有 Ability 框架。
- **行为树中的轻量级“子任务”**：在 `BTTask_RunBehavior` 节点中快速执行一个预设的 GameplayBehavior，避免为简单动作创建大量自定义任务节点。
- **多人游戏中的同步**：通过 `UNetReplicationGraph` 自动复制行为状态，减少网络同步维护成本。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/GameplayBehaviors)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/GameplayBehaviors/Source/GameplayBehaviorsTestSuite)

## 维护状态

### 近期更新

根据 git 历史记录（截止 2025-06-26）：

```text
- 2025-06-26 Added UE_INLINE_GENERATED_CPP_BY_NAME 头文件适配
- 2025-04-23 使用 LyraGame 构建目标，为所有方法/静态变量添加 DLL export
- 2025-01-16 修复 BehaviorTree 中 blackboard 资产的 ensure 报错，改为合理错误提示
- 2024-11-10 移除 #if UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_2 等废弃宏
- 2024-09-27 创建 BTTask_SetKeyValueX 引擎全部黑板键类型支持（初始提交）
```

### 维护评价

- **创建时间**：2024 年 9 月（约 1 年），属于较新的插件。
- **最近更新**：2025 年 6 月仍有功能性调整（DLL export、编译适配），说明官方仍在维护。
- **活跃度**：中等偏上，更新集中在引擎版本适配与修复，未出现废弃标记。
- **实验性状态**：`.uplugin` 中标记为 `IsBetaVersion=true`，且默认未启用，表明功能尚未稳定成熟，可能存在 API 变更。
- **推荐使用**：适合愿意承担一定不稳定风险、需要精简 AI 行为逻辑的团队。建议在项目初期进行评估，并关注后续版本升级的兼容性。