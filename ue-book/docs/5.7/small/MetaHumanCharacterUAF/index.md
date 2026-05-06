# MetaHuman Character UAF

> UAF (Unreal Animation Framework) support for MetaHuman Creator

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman UAF 组件 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（项目设置资产、蓝图） |
| 模块 | `MetaHumanCharacterUAFEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-02 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MetaHuman/MetaHumanCharacterUAF) | |

## 用途

该插件为 **MetaHuman Creator** 工具链添加了 **Unreal Animation Framework (UAF)** 支持。UAF 是 MetaHuman 在 UE5 中驱动角色动画的底层框架，负责骨骼绑定、控制绑定和动作重定向等高级功能。

此插件解决了以下核心问题：
- 在导出 MetaHuman 角色时，允许使用 UAF 作为动画框架替代传统的 Animation Blueprint（ABP）或 Control Rig 方式。
- 提供项目设置界面，让开发者可以为不同质量等级（如「电影级」「游戏级」）指定默认的角色蓝图，从而在构建 MetaHuman 时自动装配对应的 UAF 驱动。

## 使用场景

- 你正在使用 MetaHuman Creator 生成角色，并希望利用 UAF 的高性能动画绑定（例如面部表情、身体 IK 等）。
- 项目需要针对不同平台（PC / 主机 / 移动端）使用不同复杂度的 UAF 蓝图，通过质量等级自动切换。
- 你是 MetaHuman 管线的 TA 或 TD，需要将 UAF 与 MetaHuman Character 集成，并在编辑器中统一配置。

## 蓝图用法

该插件不暴露蓝图中可调用的函数或可放置的 Actor，所有功能均通过项目设置完成。开发者可在项目主菜单中选择 `Edit → Project Settings → Plugins → MetaHuman Character UAF` 进行配置。

没有可列出的蓝图节点。

## C++ 用法

插件提供了一个开发者设置类，用于在 C++ 中读取或修改 UAF 相关的默认蓝图配置。

### 头文件引入

```cpp
#include "MetaHumanCharacterUAFProjectSettings.h"
```

### 基本用法

获取当前项目设置实例，读取不同质量等级下的默认 Actor 蓝图：

```cpp
#include "MetaHumanCharacterUAFProjectSettings.h"

void SomeFunction()
{
    const UMetaHumanCharacterUAFProjectSettings* Settings = GetDefault<UMetaHumanCharacterUAFProjectSettings>();
    if (Settings)
    {
        // 检查「电影级」质量对应的蓝图
        if (const TSoftClassPtr<AActor>* Blueprint = Settings->Blueprints.Find(EMetaHumanQualityLevel::Cinematic))
        {
            // Blueprint 即为软引用，可加载使用
        }
    }
}
```

### 进阶用法

通过修改 `DefaultConfig` 来覆盖默认蓝图（仅开发阶段有效）：

```cpp
UMetaHumanCharacterUAFProjectSettings* MutableSettings = GetMutableDefault<UMetaHumanCharacterUAFProjectSettings>();
MutableSettings->Blueprints.Add(EMetaHumanQualityLevel::High, TSoftClassPtr<AActor>(FSoftClassPath("/Game/MyMH_UAF_BP.MyMH_UAF_BP_C")));
MutableSettings->SaveConfig();
```

## Demo 示例

由于插件本身仅提供配置功能，没有独立测试用例，此处提供一段最小示例代码，展示如何在模块 Startup 时读取设置并打印信息。

### MHUAFDemoModule.h

```cpp
#pragma once
#include "Modules/ModuleInterface.h"

class FMHUAFDemoModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
};
```

### MHUAFDemoModule.cpp

```cpp
#include "MHUAFDemoModule.h"
#include "MetaHumanCharacterUAFProjectSettings.h"
#include "CoreMinimal.h"

IMPLEMENT_MODULE(FMHUAFDemoModule, MHUAFDemoModule);

void FMHUAFDemoModule::StartupModule()
{
    const UMetaHumanCharacterUAFProjectSettings* Settings = GetDefault<UMetaHumanCharacterUAFProjectSettings>();
    if (Settings)
    {
        UE_LOG(LogTemp, Log, TEXT("MetaHuman Character UAF Settings loaded. Number of quality levels: %d"), Settings->Blueprints.Num());
    }
}
```

## 模块依赖

使用此插件前，你的模块需要依赖以下独特模块（Core/Engine 等常见依赖已省略）：

| 模块 | 用途 |
|---|---|
| `UAF` | Unreal Animation Framework 核心运行时 |
| `UAFAnimGraph` | UAF 的动画蓝图图支持 |
| `UAFControlRig` | UAF 的控制绑定集成 |
| `RigLogicUAF` | MetaHuman 面部表情逻辑的 UAF 驱动 |
| `MetaHumanCharacter` | MetaHuman 角色体系的基础组件 |

## 维护状态

### 近期更新

- 2025-09-29 f8c3c69d — Fix for broken BP when Common folder is redirected when exporting a UAF MH
- 2025-09-10 cd65d24c — Renamed UAF UI option
- 2025-09-02 a7cf69c2 — Move MetaHumanCharacterUAF plugin to public experimental folder

### 维护评价

该插件创建于2025年9月，属于全新发布的实验性功能。近一个月内连续有两次功能性提交（UI 重命名和导出修复），表明开发团队正在积极迭代。目前未发现被标记为废弃或已知严重问题。推荐在需要使用 UAF 驱动的 MetaHuman 项目中使用，但建议留意官方后续更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MetaHuman/MetaHumanCharacterUAF)
- [官方 MetaHuman 文档](https://dev.epicgames.com/documentation/en-us/unreal-engine/meta-human-in-unreal-engine)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MetaHuman/MetaHumanCharacterUAF/Tests)（未提供，可能位于其他位置）