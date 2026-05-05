# Blank Example Plugin

> An example of a minimal plugin. This can be used as a starting point when creating your own plugin.

| 属性 | 值 |
|---|---|
| 分类 | Examples |
| 默认启用 | false |
| 包含内容 | false |
| 模块 | BlankPlugin (Runtime) |
| 创建时间 | 2014-03-14 |
| 年龄标签 | 🏛️ 文物(>10年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/BlankPlugin) | |

## 用途

BlankPlugin 是 Epic Games 提供的**插件模板**，本身不实现任何功能。它的唯一目的是为开发者提供一个最小化的插件骨架，作为创建新插件的起点。

当你在 UE5 编辑器中通过 **Edit → Plugins → Add → Blank** 创建新插件时，生成的代码结构与 BlankPlugin 完全一致。因此它本质上是 UE5 插件开发的"Hello World"。

## 使用场景

- 你第一次学习 UE5 插件开发，需要一个最简模板来理解模块结构
- 你想快速创建一个新插件，不想从零手写 `.uplugin`、`Build.cs`、模块接口
- 你在做技术演示或教学，需要一个干净的插件骨架

## 蓝图用法

BlankPlugin 不暴露任何蓝图节点。它没有 `UFUNCTION(BlueprintCallable)` 或 `UCustomClass`，纯粹是一个空壳模块。

## C++ 用法

### 头文件引入

```cpp
#include "IBlankPlugin.h"
```

### 模块访问模式

BlankPlugin 展示了 UE5 模块的标准访问模式——单例式获取和可用性检查：

```cpp
// 检查模块是否已加载
if (IBlankPlugin::IsAvailable())
{
    // 获取模块实例
    IBlankPlugin& Module = IBlankPlugin::Get();
}
```

**来源**: `Source/BlankPlugin/Public/IBlankPlugin.h`

### 模块生命周期

```cpp
class FBlankPlugin : public IBlankPlugin
{
    virtual void StartupModule() override;   // 模块加载后执行
    virtual void ShutdownModule() override;  // 模块卸载前清理
};

IMPLEMENT_MODULE(FBlankPlugin, BlankPlugin)
```

**来源**: `Source/BlankPlugin/Private/BlankPlugin.cpp`

## Demo 示例

BlankPlugin 本身就是一个完整的最小示例。要基于它创建你自己的插件：

1. 复制 `Engine/Plugins/Developer/BlankPlugin/` 整个目录
2. 重命名目录和所有内部文件（替换 `BlankPlugin` 为你的插件名）
3. 修改 `.uplugin` 中的 `FriendlyName`、`Description` 等元数据
4. 在 `Build.cs` 中添加你需要的模块依赖
5. 在 `StartupModule()` / `ShutdownModule()` 中编写初始化逻辑

### 最小 Build.cs 依赖

```csharp
public class BlankPlugin : ModuleRules
{
    public BlankPlugin(ReadOnlyTargetRules Target) : base(Target)
    {
        PublicDependencyModuleNames.AddRange(new string[] { "Core" });
    }
}
```

**来源**: `Source/BlankPlugin/BlankPlugin.Build.cs`

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | UE5 核心模块，提供基础类型、模块管理等 |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 2023-01-16 | `7ce67da` | IWYU 更新，减少不必要的 #include | 代码清理，无功能变更 |
| 2022-11-07 | `0a10c21` | Release-Engine-Staging 批量更新 | 批量同步，非针对性改动 |
| 2019-12-27 | `28d3d74` | 版权声明更新 | 纯文本替换，无代码变更 |

### 维护评价

BlankPlugin 自 2014 年创建以来，最近一次实质性更新已是 3 年前（2023 年的 IWYU 清理），且那也仅是编译层面的 include 优化，不涉及功能变更。近 7 年（2019-2026）没有任何功能性提交。

不过考虑到这是一个**静态模板**，不维护是正常的——它的结构在 UE5 时代依然有效，不需要频繁更新。

**评价**: 稳定的静态模板，无需关注维护状态。适合作为学习和起步使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/BlankPlugin)
- [官方文档]()（无）
- [测试用例]()（无——模板插件没有测试用例）
