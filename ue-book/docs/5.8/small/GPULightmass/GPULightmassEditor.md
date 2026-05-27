# GPU Lightmass

> Static lighting building & previewing system using DXR

| 属性 | 值 |
|---|---|
| 中文名 | GPU 光照贴图 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（内容资源） |
| 模块 | `GPULightmass` (UncookedOnly), `GPULightmassEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-06-23 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GPULightmass) | |

## 用途

GPULightmass 是传统 CPU 光照烘焙系统 Lightmass 的 **GPU 加速替代方案**，利用 DirectX Raytracing (DXR) 硬件光线追踪技术构建静态光照贴图（Lightmap）。

**解决的核心问题：**

- 传统 Lightmass 使用 CPU 进行全局光照计算，大型场景烘焙需要数小时
- GPULightmass 利用 RTX 等硬件加速，将烘焙时间从小时级缩短到分钟级
- 支持 "Bake What You See" 模式，可在编辑器视口中实时预览光照烘焙进度

**技术原理：** 通过 DXR 发射大量光线，计算场景中的直接光照和间接光照（多次反弹），结果写入 Lightmap 纹理。使用 Shader Binding Table (SBT) 管理光线追踪着色器绑定。

**限制条件：**

- 仅支持 **Win64** 平台
- 需要支持 DXR 的显卡（NVIDIA RTX 20 系列及以上）
- 当前为实验性（Beta）状态，功能可能不完整

## 使用场景

- 你有一个大型开放世界场景，传统 Lightmass 烘焙需要数小时 → 用 GPULightmass 加速到分钟级
- 你有 RTX 显卡并希望利用硬件光线追踪加速光照构建 → 用 GPULightmass
- 你需要在编辑器中实时预览静态光照效果 → 用 GPULightmass 的 Bake What You See 模式
- 你正在 Win64 平台开发需要高质量静态光照的游戏 → 用 GPULightmass

## 蓝图用法

GPULightmass 是一个编辑器烘焙系统，**没有暴露 BlueprintCallable API**。所有操作通过编辑器 UI 完成：

1. **启用插件：** 在 Edit → Plugins 中搜索 "GPU Lightmass" 并启用（默认关闭）
2. **打开设置面板：** 菜单栏 → Window → GPU Lightmass Settings
3. **启动烘焙：** 菜单栏 → Build → GPU Lightmass Build（或点击设置面板的 Start 按钮）
4. **保存并停止：** 点击 "Save and Stop" 按钮保存当前进度
5. **取消烘焙：** 点击 "Cancel" 按钮丢弃当前进度

### 设置面板功能

| 功能 | 说明 |
|---|---|
| Realtime 模式 | 开启后视口实时更新光照预览 |
| Bake What You See | 按当前视口角度进行优先烘焙 |
| 启动烘焙 | 开始 GPU 光照构建 |
| 保存并停止 | 保存已烘焙部分并停止 |
| 取消 | 丢弃当前烘焙进度 |

## C++ 用法

GPULightmass 的编辑器模块提供了基础的模块接口，主要用于编辑器集成。

### 头文件引入

```cpp
#include "GPULightmassEditorModule.h"
```

### 基本用法

```cpp
// 获取编辑器模块实例
FGPULightmassEditorModule& EditorModule = 
    FModuleManager::GetModuleChecked<FGPULightmassEditorModule>("GPULightmassEditor");

// 查询 GPU Lightmass 状态
bool bIsRunning = FGPULightmassEditorModule::IsRunning();
bool bIsRealtime = FGPULightmassEditorModule::IsRealtimeOn();
bool bIsBakeWhatYouSee = FGPULightmassEditorModule::IsBakeWhatYouSeeMode();
```

来源：`Source/GPULightmassEditor/Private/GPULightmassEditorModule.h`

## Demo 示例

GPULightmass 主要通过编辑器 UI 操作，无独立运行时示例。以下展示如何在 C++ 中查询其状态：

```cpp
// MyLightingTool.h
#pragma once

#include "CoreMinimal.h"

class FMyLightingTool
{
public:
    // 检查 GPU Lightmass 是否可用
    static bool IsGPULightmassAvailable();
    
    // 获取烘焙状态信息
    static FString GetBakeStatus();
};
```

```cpp
// MyLightingTool.cpp
#include "MyLightingTool.h"
#include "GPULightmassEditorModule.h"
#include "Modules/ModuleManager.h"

bool FMyLightingTool::IsGPULightmassAvailable()
{
    return FModuleManager::Get().IsModuleLoaded("GPULightmassEditor");
}

FString FMyLightingTool::GetBakeStatus()
{
    if (!IsGPULightmassAvailable())
    {
        return TEXT("GPU Lightmass 未加载");
    }
    
    if (FGPULightmassEditorModule::IsRunning())
    {
        return FGPULightmassEditorModule::IsBakeWhatYouSeeMode() 
            ? TEXT("烘焙中（Bake What You See）") 
            : TEXT("烘焙中");
    }
    
    return TEXT("空闲");
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `D3D12RHI` | DirectX 12 渲染硬件接口（DXR 依赖） |
| `RenderCore` | 渲染核心基础设施 |
| `RHI` | 渲染硬件抽象层 |
| `MeshDescription` | 网格数据处理 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `78d4e656` | [GPULM] Flush deferred SBT static-range frees on cached scene teardown | 优化缓存场景销毁时的 SBT 静态范围资源释放 |
| 2026-05-12 | `98b3c0ef` | [HWRT] Add MeshBatchesView to FRayTracingDynamicGeometryUpdateParams and unify mesh batch ownership. | 光线追踪动态几何更新参数重构，统一网格批次所有权 |
| 2026-04-21 | `a437915f` | [HWRT] Refactored shared vertex buffer management in FRayTracingDynamicGeometryUpdateManager. | 重构光线追踪动态几何管理器的共享顶点缓冲区 |
| 2026-04-15 | `2a295e97` | - Removed BlockUntilGPUIdle and SubmitCommandsAndFlushGPU in place of SubmitAndBlockUntilGPUIdle | 统一 GPU 同步 API，移除旧接口 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移至新格式 |

### 维护评价

- **维护状态：活跃维护中** — 2026 年 5 月仍有功能性更新
- **实验性状态** — 仍标记为 Beta，`EnabledByDefault=false`
- **平台限制** — 仅 Win64，需 DXR 硬件支持
- **技术债务** — 部分更新为底层渲染 API 重构（HWRT 基础设施统一），表明 Epic 持续投入 GPU 光线追踪基础设施

**推荐程度：⭐⭐⭐ 中等推荐**

适合在 Win64 + RTX 硬件环境下加速光照烘焙。但作为实验性插件，生产环境使用需注意稳定性。如果项目对光照烘焙速度有较高要求且硬件条件满足，值得尝试。建议配合传统 Lightmass 作为备选方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GPULightmass)
- 官方文档：无
- [GPU Lightmass 论坛讨论](https://forums.unrealengine.com/gpu-lightmass)（社区资源）