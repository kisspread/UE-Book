# LightWeightInstancesEditor

> Light Weight Instances provide the flexibility and interaction of actors while having performance similar to instanced meshes.

| 属性 | 值 |
|---|---|
| 中文名 | 轻量级实例编辑器 |
| 分类 | Other |
| 默认启用 | ❌ 否（实验性插件，需手动启用） |
| 包含内容 | ❌ 无 |
| 模块 | `LightWeightInstancesEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-01-16 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/LightWeightInstancesEditor) | |

## 用途

该插件为 **Light Weight Instances (LWI)** 提供编辑器支持。LWI 是一种将 Actor 的灵活性与实例化网格的性能相结合的中间方案：它允许场景中放置大量可交互的动态对象（如可拾取物品、小型装饰物），同时利用实例化渲染减少 Draw Call。

插件主要功能是在关卡视口上下文菜单中添加“Convert <actors> to light weight instances”选项，允许设计师将选中的同类 Actor 批量转换为 LWI，同时自动处理数据层（Data Layers）等关联设置。

## 使用场景

- 在大世界中放置大量可交互的小物体（如硬币、药水瓶、碎石），既希望它们能像 Actor 一样响应碰撞和脚本，又希望保持较高的渲染性能。
- 需要将已有的同类 Actor 快速转换为轻量级实例，而不必手动替换为 ISM 组件。
- 配合数据层管理，实现 LWI 的按需加载/卸载。

## 蓝图用法

本插件为编辑器模块，不提供任何蓝图可调用节点。转换操作通过视口右键菜单手动触发。

## C++ 用法

### 头文件引入

```cpp
#include "LightWeightInstancesEditor.h"
```

### 基本用法

插件启动后自动注册上下文菜单扩展。如需在 C++ 中主动转换 Actor，可调用模块内部方法：

```cpp
// 获取模块实例
FLightWeightInstancesEditorModule& Module = FModuleManager::LoadModuleChecked<FLightWeightInstancesEditorModule>("LightWeightInstancesEditor");
// 注意：ConvertActorsToLWIsUIAction 是私有方法，不能直接外部调用。
// 实际转换由菜单命令代理执行，通过反射机制调用。
```

> 来源：`LightWeightInstancesEditor.h` 中定义 `ConvertActorsToLWIsUIAction` 为私有成员，仅由 `CreateLevelViewportContextMenuExtender` 中的委托调用。

### 进阶用法

若想自定义转换逻辑，需要在编辑器模块的 `StartupModule` 中注册自己的 `FExtender`，参照 `AddLevelViewportMenuExtender` 的实现方式：

```cpp
void MyEditorModule::StartupModule()
{
    // 获取全局 Level Editor Actions
    FLevelEditorModule& LevelEditorModule = FModuleManager::LoadModuleChecked<FLevelEditorModule>("LevelEditor");
    
    // 创建扩展器
    TSharedRef<FExtender> MenuExtender = MakeShareable(new FExtender);
    MenuExtender->AddMenuExtension(
        "ActorTypeTools",
        EExtensionHook::After,
        nullptr,
        FMenuExtensionDelegate::CreateRaw(this, &FMyEditorModule::BuildMenu)
    );
    
    // 注册
    LevelEditorModule.GetAllLevelViewportContextMenuExtenders().Add(MenuExtender);
}
```

本插件的 `CreateLevelViewportContextMenuExtender` 内部执行了：
1. 过滤选中的 Actor 是否属于同一类型（`GetClass` 相同）。
2. 检查是否存在可用的 LWI 管理器（可通过 CVar `LWI.Editor.GridSize` 控制网格大小）。
3. 处理数据层引用。
4. 调用引擎内部的转换逻辑。

## Demo 示例

以下是一个最小编辑器模块示例，演示如何使用该插件的菜单扩展（需配合启用 LightWeightInstancesEditor 插件）：

```cpp
// MyEditorModule.h
#pragma once
#include "Modules/ModuleManager.h"

class FMyEditorModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    TSharedRef<FExtender> CreateMyMenuExtender(const TSharedRef<FUICommandList> CommandList, const TArray<AActor*> InActors);
    void MyConversionAction(const TArray<AActor*> InActors);
    FDelegateHandle MyExtenderHandle;
};
```

```cpp
// MyEditorModule.cpp
#include "MyEditorModule.h"
#include "LevelEditor.h"
#include "Framework/MultiBox/MultiBoxBuilder.h"

#define LOCTEXT_NAMESPACE "FMyEditorModule"

void FMyEditorModule::StartupModule()
{
    // 借用 LightWeightInstancesEditor 的扩展点，在 Actor 上下文菜单中添加自定义选项
    FLevelEditorModule& LevelEditorModule = FModuleManager::LoadModuleChecked<FLevelEditorModule>("LevelEditor");
    auto& MenuExtenders = LevelEditorModule.GetAllLevelViewportContextMenuExtenders();
    MenuExtenders.Add(FLevelEditorModule::FLevelViewportMenuExtender_SelectedActors::CreateRaw(this, &FMyEditorModule::CreateMyMenuExtender));
    MyExtenderHandle = MenuExtenders.Last().GetHandle();
}

void FMyEditorModule::ShutdownModule()
{
    if (FLevelEditorModule* LevelEditorModule = FModuleManager::GetModulePtr<FLevelEditorModule>("LevelEditor"))
    {
        LevelEditorModule->GetAllLevelViewportContextMenuExtenders().RemoveAll([this](const FLevelEditorModule::FLevelViewportMenuExtender_SelectedActors& Extender)
        {
            return Extender.GetHandle() == MyExtenderHandle;
        });
    }
}

TSharedRef<FExtender> FMyEditorModule::CreateMyMenuExtender(const TSharedRef<FUICommandList> CommandList, const TArray<AActor*> InActors)
{
    TSharedRef<FExtender> Extender = MakeShareable(new FExtender);
    Extender->AddMenuExtension(
        "ActorTypeTools",
        EExtensionHook::After,
        nullptr,
        FMenuExtensionDelegate::CreateLambda([InActors](FMenuBuilder& MenuBuilder)
        {
            MenuBuilder.AddMenuEntry(
                LOCTEXT("MyConversionAction", "My Convert"),
                LOCTEXT("MyConversionActionTooltip", "Example conversion"),
                FSlateIcon(),
                FUIAction(FExecuteAction::CreateLambda([InActors]()
                {
                    // 此处可调用 LightWeightInstancesEditor 的内部逻辑，但私有 API 需反射或拷贝代码
                    UE_LOG(LogTemp, Warning, TEXT("Converting %d actors"), InActors.Num());
                })),
                NAME_None,
                EUserInterfaceActionType::Button
            );
        })
    );
    return Extender;
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FMyEditorModule, MyEditorModule)
```

> 注意：此示例仅为展示扩展模式，实际转换需依赖 `LightWeightInstancesEditor` 的内部实现。建议直接使用插件已提供的官方菜单项。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `DataLayerEditor` | 支持数据层（Data Layers）相关的编辑器操作，LWI 转换时需处理数据层信息 |

其他依赖均为常见模块（Core, CoreUObject, Engine, Slate, SlateCore, UnrealEd, Projects 等），此处省略。

## 维护状态

### 近期更新

- 2023-06-14 `d1f48fc5` Fix implicit capture of this using [=] deprecated in C++20
- 2023-03-30 `c2e52fac` Avoid nullptr dereference during "Convert <actors> to light weight instances" if data layers aren't available
- 2023-02-16 `0b766b6f` Fix missing LWI editor file from CL 24263247
- 2023-02-16 `8ba29c35` Allow the creation of light weight instance managers in a grid set by the cvar `LWI.Editor.GridSize`
- 2023-01-16 `bbc37aa2` [Engine/Plugins] 初始提交

### 维护评价

- **创建时间**：2023年1月，距今约3年。
- **近期更新**：最后一次实质性功能更新是2023年2月（网格大小 CVar），后续两次为编译问题修复。距今已超过1年无功能更新。
- **活跃度**：不活跃。插件仍处于实验性阶段（`IsBetaVersion=true`），且 `EnabledByDefault=false`，表明官方对其成熟度有所保留。
- **潜在问题**：已知存在数据层为 nullptr 时的崩溃风险（已修复），但整体功能较简单，可能在未来版本中被重构或废弃。
- **推荐使用**：如果项目需要使用轻量级实例系统，可以启用该插件。但需注意其为实验性，不保证长期兼容性。对于大规模生产项目，建议谨慎评估或自行封装类似功能。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/LightWeightInstancesEditor)
- [官方文档（暂无）]
- [测试用例（该插件无独立测试目录）]