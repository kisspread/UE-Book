# Packed Attributes

> ⚠️ **此插件已被移除**（2025-10-17），仅作为存根存在，从未包含实际功能代码。

| 属性 | 值 |
|---|---|
| 分类 | Animation (Experimental) |
| 默认启用 | false |
| 包含内容 | true |
| 模块 | PackedAttributes (Runtime), PackedAttributesTestSuite (UncookedOnly) |
| 创建时间 | 2024-10-18 |
| 年龄标签 | 🆕 |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Animation/PackedAttributes) | 已在 5.6 之后移除 |

## 用途

PackedAttributes 是一个**从未完成的存根插件**（Stub），由 Epic Games 的 Nicholas Frechette 创建，计划用于实现动画系统中的"打包属性"（Packed Attributes）运行时功能。从命名空间 `UE::Anim::PackedAttributes` 可以看出，它属于动画子系统的一部分。

插件创建时的 commit message 为 _"Add stub for new Compact Attribute Runtime plugin"_，对应的 JIRA 任务为 `UE-224234`。然而，该插件在长达一年的时间里始终只有空壳模块代码，没有任何实际实现，最终于 2025-10-17 被移除，commit message 为 _"Remove PackedAttributes plugin, no longer needed"_。

### 什么是 Packed Attributes？

虽然插件本身没有实现，但从命名和上下文推断，"Packed Attributes" 可能指的是：
- **紧凑化动画属性存储**：将多个小属性（如骨骼权重、自定义数据等）打包到更少的内存位中，减少内存占用和带宽消耗
- **GPU 动画数据优化**：将动画属性以压缩格式传输到 GPU，提升顶点动画和骨骼动画的渲染效率

这些概念在现代游戏引擎中很常见（如 Unreal 的 `FPackedNormal`、`FPackedRGBA16N` 等），但该插件从未实现其规划功能。

## 使用场景

**不适用** — 此插件已被移除，无法使用。

## 蓝图用法

无。插件不包含任何 `UFUNCTION(BlueprintCallable)` 或 `UPROPERTY(BlueprintReadWrite)` 接口。

## C++ 用法

### 头文件引入

无公共头文件。插件仅包含模块注册代码，没有对外暴露的 API。

### 基本用法

插件的 Runtime 模块仅包含一个空壳 `IModuleInterface`：

```cpp
// Source/Runtime/Private/PackedAttributes/Module.cpp
namespace UE::Anim::PackedAttributes
{
    class FRuntimeModule : public IModuleInterface
    {
    public:
        virtual void StartupModule() override {}
        virtual void ShutdownModule() override {}
    };
}
```

## Demo 示例

不适用 — 插件无功能实现。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎运行时 |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-10-17 | `34fdd3e` | Remove PackedAttributes plugin, no longer needed | Epic 决定该插件不再需要，从源码树中移除 |
| 2024-10-18 | `a2b5cdd` | Add stub for new Compact Attribute Runtime plugin | 初始创建，仅包含空壳模块代码，JIRA: UE-224234 |

### 维护评价

**状态：已废弃/已移除 ❌**

- **创建时间**：2024-10-18，作为存根提交
- **生命周期**：仅存活约 1 年（2024-10 → 2025-10）
- **代码量**：始终只有模块注册文件（Module.cpp + Build.cs），无实际功能代码
- **移除原因**：commit message 明确标注 _"no longer needed"_，说明 Epic 内部决定取消该功能的独立插件化，可能是因为：
  - 功能被整合到其他模块（如动画核心模块）
  - 方案被重新设计，不再需要独立插件
  - 优先级降低，资源投入到其他方向

**不推荐使用** — 该插件已不存在于最新源码中，且从未提供过可用功能。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Animation/PackedAttributes)（已移除，链接仅适用于 UE 5.5 及之前版本）
- [初始提交](https://github.com/EpicGames/UnrealEngine/commit/a2b5cdd152cf) — 添加存根
- [移除提交](https://github.com/EpicGames/UnrealEngine/commit/34fdd3e52f8a) — 移除插件
