# State Tree

> General purpose hierarchical state machine

| 属性 | 值 |
|---|---|
| 中文名 | 状态树 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（状态树资产） |
| 模块 | `StateTreeModule` (Runtime), `StateTreeEditorModule` (Runtime), `StateTreeDeveloper` (Runtime), `StateTreeTestSuite` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2021-09-28 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/StateTree) | |

## 用途

StateTree 是 Unreal Engine 的通用层级状态机（Hierarchical State Machine）系统，用于替代或补充传统行为树（Behavior Tree）方案。它提供了可视化编辑器，支持复杂的状态逻辑、条件转换、任务执行和属性绑定。

与 Behavior Tree 相比，StateTree 的核心优势：
- **层级状态结构**：支持嵌套状态和并发执行
- **属性绑定系统**：节点间数据可直接绑定，无需手动传递
- **通用性**：不仅限于 AI，可驱动任意游戏逻辑（动画、游戏流程、环境系统等）
- **可视化编辑**：完整的编辑器支持，包括状态图、转换条件、调试工具

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| `StateTreeModule` | Runtime | 核心运行时模块，包含状态树执行引擎、节点基类、属性绑定系统 |
| `StateTreeEditorModule` | Runtime | 编辑器模块，提供状态树可视化编辑器和资产类型支持 |
| `StateTreeDeveloper` | Runtime | 开发者工具模块，提供调试和开发辅助功能 |
| `StateTreeTestSuite` | Runtime | 测试模块，包含完整的单元测试和集成测试 |

## 使用场景

- **AI 行为系统**：替代 Behavior Tree，实现更灵活的 AI 决策逻辑
- **游戏流程管理**：控制游戏阶段（菜单、加载、游戏、暂停等）的转换
- **动画状态机**：驱动复杂的动画逻辑和转换条件
- **环境系统**：管理环境事件、天气系统、昼夜循环等状态
- **任务系统**：实现任务状态跟踪和条件触发

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `StartLogic` | 启动状态树逻辑 | `UStateTreeComponent` |
| `StopLogic` | 停止状态树逻辑 | `UStateTreeComponent` |
| `RestartLogic` | 重启状态树 | `UStateTreeComponent` |
| `GetStateTreeRunStatus` | 获取当前运行状态 | `UStateTreeComponent` |

### 使用示例

1. **添加组件**：在 Actor 上添加 `UStateTreeComponent`
2. **指定资产**：在组件属性中设置要执行的 StateTree 资产
3. **启动逻辑**：调用 `StartLogic` 开始执行状态树
4. **监听事件**：通过事件接口响应状态变化

## C++ 用法

### 头文件引入

```cpp
#include "StateTreeModule.h"
#include "StateTreeComponent.h"
#include "StateTreeExecutionContext.h"
```

### 基本用法

```cpp
// 获取状态树组件并启动逻辑
UStateTreeComponent* StateTreeComp = Actor->FindComponentByClass<UStateTreeComponent>();
if (StateTreeComp)
{
    StateTreeComp->StartLogic();
}
```

### 进阶用法

```cpp
// 自定义状态树节点
UCLASS()
class UMyStateTreeTask : public UStateTreeTaskBase
{
    GENERATED_BODY()
    
    virtual EStateTreeRunStatus EnterState(FStateTreeExecutionContext& Context) const override;
    virtual void ExitState(FStateTreeExecutionContext& Context) const override;
};
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AIModule` | AI 相关功能支持 |
| `GameplayAbilities` | 游戏技能系统集成 |
| `SmartObjectsModule` | 智能对象系统交互 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `2c528ff3` | [StateTree] Fix invalid memory access. | 修复无效内存访问问题 |
| 2026-05-14 | `fbc95955` | [StateTree] Fix bas memory access in unittest | 修复单元测试中的内存访问错误 |
| 2026-05-14 | `4efd5cdb` | [StateTree] Compile pending StateTree assets in the editor before linking. This prevents link failure | 编辑器中链接前编译待处理的状态树资产，防止链接失败 |
| 2026-05-13 | `541c19e0` | Extend property binding compatibility to support task completion bindings | 扩展属性绑定兼容性，支持任务完成绑定 |
| 2026-05-12 | `ea25bb3b` | [StateTree] Copy-paste transition also copies the bindings. Fix the UI that displays the list of sta | 复制粘贴转换时同时复制绑定，修复状态列表显示 UI |

### 维护评价

**活跃维护** ✅

- 创建于 2021 年，已稳定发展约 4 年
- 最近 1 个月内有多次实质性更新（内存修复、功能增强）
- 持续修复 bug 和改进功能，处于活跃开发状态
- 版本号 0.1 表示仍在迭代中，API 可能有变动
- **推荐使用**：适用于需要灵活状态逻辑的项目，但需注意版本更新

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/StateTree)
- [StateTreeModule 文档](StateTreeModule.md)
- [StateTreeEditorModule 文档](StateTreeEditorModule.md)
- [StateTreeDeveloper 文档](StateTreeDeveloper.md)
- [StateTreeTestSuite 文档](StateTreeTestSuite.md)