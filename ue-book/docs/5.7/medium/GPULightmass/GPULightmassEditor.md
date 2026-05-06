# GPU Lightmass

> Static lighting building & previewing system using DXR

| 属性 | 值 |
|---|---|
| 中文名 | GPU 光体 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（光照构建缓存与设置） |
| 模块 | `GPULightmass` (UncookedOnly), `GPULightmassEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-02 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/GPULightmass) | |

## 用途

GPU Lightmass 插件利用 DXR（DirectX Raytracing）硬件加速，在编辑器中提供**实时、渐进式**的静态光照构建与预览。它替代了传统的 CPU Lightmass，允许美术和设计师在调整光照后无需漫长烘焙，即可即时看到高质量的光照贴图结果，大幅缩短迭代周期。该插件特别适合需要频繁调整静态光照（如关卡照明、烘培阴影）的团队。

## 使用场景

- 你正在制作一个需要高质量静态光照（如室内场景、建筑可视化）的关卡，并且希望每次修改光照后快速预览效果。
- 你希望保留静态光照的灵活性，同时获得接近实时的反馈，而不是等待传统的 CPU 烘焙。
- 你的项目使用 DXR 兼容的 GPU（NVIDIA RTX 系列或 AMD RX 6000 系列及以上），且平台为 Windows 64 位。
- 你需要“所见即所得”（WYSIWYG）的静态光照调试体验——例如，调整间接光照强度或阴影锐度后立即看到变化。

## 蓝图用法

该插件**没有暴露任何蓝图可调用节点**。所有交互集中在编辑器界面，通过以下方式操作：

1. **启用插件**：在 Edit → Plugins → Experimental → GPU Lightmass 中启用。
2. **启动构建**：在主菜单的 Build 下选择 **Lightmass (GPU)**，或通过自定义工具栏按钮（需手动添加）。
3. **实时预览**：在 Lightmass 设置面板中勾选 **Bake What You See** 模式，灯光调整后会自动更新。

> 若需通过蓝图控制构建流程，建议使用 `UEditorLevelLibrary` 中的静态函数（如 `BuildLighting`），但该函数仅触发标准构建，而非 GPU Lightmass。

| 节点 | 说明 | 所在类 |
|---|---|---|
| 无暴露节点 | — | — |

## C++ 用法

### 头文件引入

```cpp
#include "GPULightmassEditorModule.h"
```

### 基本用法

通过 `FGPULightmassEditorModule` 访问模块功能，主要用于编程式触发构建或获取状态。

```cpp
// 获取模块实例
FGPULightmassEditorModule& Module = FModuleManager::LoadModuleChecked<FGPULightmassEditorModule>("GPULightmassEditor");

// 模拟点击“开始构建”按钮
Module.OnStartClicked();

// 检查是否正在运行
bool bIsRunning = Module.IsRunning();

// 检查是否处于“烘焙所见即所得”模式
bool bWYSIWYG = Module.IsBakeWhatYouSeeMode();

// 取消当前构建
Module.OnCancelClicked();

// 保存并停止构建
Module.OnSaveAndStopClicked();
```

**文件来源**: `Source/GPULightmassEditor/Private/GPULightmassEditorModule.h`

### 进阶用法

通过扩展编辑器菜单或添加工具栏按钮，与 GPU Lightmass 交互。例如，在自定义模块中为 `FExtender` 添加构建菜单项：

```cpp
// 在自定义模块的 StartupModule 中
void FMyEditorModule::StartupModule()
{
    // 获取 LevelEditor 模块的菜单扩展点
    FLevelEditorModule& LevelEditorModule = FModuleManager::LoadModuleChecked<FLevelEditorModule>("LevelEditor");
    TSharedRef<FExtender> Extender = MakeShareable(new FExtender);
    Extender->AddMenuExtension(
        "BuildLighting", // 扩展点名称
        EExtensionHook::After,
        nullptr,
        FMenuExtensionDelegate::CreateRaw(this, &FMyEditorModule::AddGPULightBuildMenu)
    );
    LevelEditorModule.GetMenuExtensibilityManager()->AddExtender(Extender);
}

void FMyEditorModule::AddGPULightBuildMenu(FMenuBuilder& MenuBuilder)
{
    MenuBuilder.BeginSection("GPULightmass", LOCTEXT("GPULightmassSection", "GPU Lightmass"));
    MenuBuilder.AddMenuEntry(
        LOCTEXT("StartGPUBuild", "Start GPU Lightmass Build"),
        LOCTEXT("StartGPUBuildTooltip", "Start building static lighting using DXR"),
        FSlateIcon(),
        FUIAction(FExecuteAction::CreateLambda([]() {
            FGPULightmassEditorModule& Module = FModuleManager::LoadModuleChecked<FGPULightmassEditorModule>("GPULightmassEditor");
            Module.OnStartClicked();
        }))
    );
    MenuBuilder.EndSection();
}
```

**文件来源**: 基于 `FGPULightmassEditorModule::OnExtendLevelEditorBuildMenu` 的反向设计（源文件未完全展示，但接口声明类似）。

## Demo 示例

提供一个最小的编辑器模块，用于在编辑器启动时自动触发 GPU Lightmass 预览构建（谨慎使用，仅作演示）。创建插件 `MyGPULightDemo`，包含以下文件：

### `MyGPULightDemo.h`
```cpp
#pragma once
#include "CoreMinimal.h"
#include "Modules/ModuleInterface.h"

class FMyGPULightDemoModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

### `MyGPULightDemo.cpp`
```cpp
#include "MyGPULightDemo.h"
#include "GPULightmassEditorModule.h"

IMPLEMENT_MODULE(FMyGPULightDemoModule, MyGPULightDemo)

void FMyGPULightDemoModule::StartupModule()
{
    // 在编辑器启动后延迟 5 秒自动开始 GPU Lightmass 构建（仅用于演示，实际中不建议自动调用）
    if (GEditor)
    {
        FTimerHandle TimerHandle;
        GEditor->GetTimerManager()->SetTimer(TimerHandle, FTimerDelegate::CreateLambda([]()
        {
            if (FGPULightmassEditorModule* Module = FModuleManager::GetModulePtr<FGPULightmassEditorModule>("GPULightmassEditor"))
            {
                UE_LOG(LogTemp, Log, TEXT("Auto-starting GPU Lightmass build..."));
                Module->OnStartClicked();
            }
        }), 5.0f, false);
    }
}

void FMyGPULightDemoModule::ShutdownModule()
{
}
```

**说明**：此示例展示了如何在 C++ 中访问 GPU Lightmass 模块并调用其构建命令。实际使用时应通过 Editor UI 触发，避免自动构建。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `GPULightmass` | 核心渲染与构建逻辑（UncookedOnly 模块） |
| `LevelEditor` | 扩展 Build 菜单（仅在编辑器模块中） |
| `UnrealEd` | 编辑器基础架构 |
| `Renderer` | 渲染管线与 DXR 集成 |
| `RayTracing` | DXR 支持（间接依赖） |

> 仅在 `GPULightmassEditor.Build.cs` 中显式列出的依赖已省略标准模块（Core, Engine, Slate 等）。实际构建时还需要 `Projects` 和 `DeveloperSettings`。

## 维护状态

### 近期更新

- 2025-11-18 e716f9a2 — [Ray Tracing] Fix a bug in the build instance buffer pass where incorrect GPU scene resources are used
- 2025-09-12 9bd0ee67 — Landscape Editor - Retopologize / XY offset removal
- 2025-09-10 d4775540 — Updated LightmapRenderer to also use MeshBatch.SegmentIndex when setting up bindings.
- 2025-09-10 20d3b102 — [HWRT] Fix crash in FRayTracingDynamicGeometryUpdateManager due to missing VertexFactory when skeletal mesh is dynamically updated
- 2025-09-02 b125c860 — Fix bug in LightmapRenderer when using RequiresSeparateHitGroupContributionsBuffer

### 维护评价

- **创建时间**：2025-09-02（约 3 个月）
- **更新频率**：近 3 个月有多次 bug 修复和功能调整，2025-11-18 仍有提交，表明当前处于活跃维护状态。
- **状态**：标记为实验性（beta），默认禁用，仅支持 Windows x64 和 DXR 硬件。
- **已知限制**：
  - 不支持 macOS/Linux。
  - 需要兼容 DXR 的 GPU 和驱动程序。
  - 某些复杂场景（如大量半透明物体、曲面细分）可能产生不一致的结果。
  - 构建结果与 CPU Lightmass 不完全一致（但质量通常相当）。
- **推荐使用**：适合对硬件有控制权且追求快速迭代的团队。建议在项目早期启用测试，并备有 CPU Lightmass 作为回退方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/GPULightmass)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/gpu-lightmass-in-unreal-engine/)（如适用）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/GPULightmass/Tests)（如果存在，通常位于 `Engine/Tests` 目录）