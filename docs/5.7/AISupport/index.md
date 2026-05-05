# AISupport

> A simple plugin that makes sure your project loads AIModule and NavigationSystem at runtime

| 属性 | 值 |
|---|---|
| 分类 | AI |
| 默认启用 | true |
| 包含内容 | false |
| 模块 | AISupportModule (Runtime, PostConfigInit) |
| 创建时间 | 2018-04-16 |
| 年龄标签 | 👴 老古董(>5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/AI/AISupport) | |

## 用途

AISupport 是一个**纯胶水插件**，它的唯一职责是确保 AIModule 和 NavigationSystem 的 DLL 在引擎启动早期就被加载到内存中。

核心机制：在 `PostConfigInit` 加载阶段（非常早），通过调用 `FAIResources::GetResourcesCount()` 强制链接 AIModule 的符号，使操作系统提前加载 AIModule.dll 和 NavigationSystem.dll。如果不这样做，这些 DLL 可能在实际使用时才被懒加载，导致依赖时序问题。

插件本身**不提供任何 AI 功能**，只是一个加载保障机制。

## 使用场景

- 你的项目启用了 AI 功能（行为树、EQS、导航系统等）→ 通常已经自动启用此插件
- 你在开发 AI 相关插件，需要确保 AIModule 在引擎初始化早期就可用 → 依赖此插件
- 遇到 AIModule/NavigationSystem DLL 加载时序问题 → 检查此插件是否启用

## 蓝图用法

此插件不暴露任何蓝图接口。它是一个纯内部加载保障模块。

## C++ 用法

此插件不提供公开的 API。它的全部代码仅在模块启动时执行一行强制链接：

```cpp
// AISupportModule.cpp - 完整实现（去掉版权头）
#include "AISupportModule.h"
#include "AITypes.h"

class FAISupportModule : public IAISupportModule
{
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};

void FAISupportModule::StartupModule()
{
    // 强制链接 AI 模块符号，确保 DLL 提前加载
    static int32 ForceLink = FAIResources::GetResourcesCount();
    ForceLink++;
}
```

如需在代码中检查模块是否可用：

```cpp
#include "AISupportModule.h"

if (IAISupportModule::IsAvailable())
{
    // AISupport 已加载，AIModule 和 NavigationSystem DLL 已就绪
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | 引擎核心 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎基础 |
| `AIModule` | AI 行为树、EQS 等（本插件要确保它被加载） |
| `NavigationSystem` | 导航网格、寻路（本插件要确保它被加载） |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 |
|---|---|---|
| 2024-10-22 | `98a8e0e0` | 移除 UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_2 宏作用域 |
| 2023-01-13 | `3c9aacb1` | IWYU 清理公共头文件，移除不必要的 include |
| 2023-01-12 | `2f78497e` | IWYU 清理私有文件 |

所有近期更新均为 IWYU/include 清理和编译兼容性维护，无功能性变更。

### 维护评价

此插件功能极其简单（约 10 行有效代码），自 2018 年创建以来从未有过功能变更，也不需要——它是一个纯基础设施胶水模块。近期的 commit 都是跟随引擎的 IWYU 清理工作。该插件属于"稳定不变"状态，不是被废弃，而是**功能已定型**。

✅ 推荐保持启用（默认已启用），除非你明确不需要 AI 功能。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/AI/AISupport)
