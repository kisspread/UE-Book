# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo

| 属性 | 值 |
|---|---|
| 中文名 | 多机同步渲染 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（配置资产、着色器、第三方库） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterColorGrading` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterConfigurator` (Runtime), `DisplayClusterDetails` (Runtime), `DisplayClusterEditor` (Runtime), `DisplayClusterFillDerivedDataCache` (Runtime), `DisplayClusterLightCardEditor` (Runtime), `DisplayClusterLightCardEditorShaders` (Runtime), `DisplayClusterMedia` (Runtime), `DisplayClusterMediaEditor` (Runtime), `DisplayClusterMessageInterception` (Runtime), `DisplayClusterMonitor` (Runtime), `DisplayClusterMonitorEditor` (Runtime), `DisplayClusterMoviePipeline` (Runtime), `DisplayClusterMoviePipelineEditor` (Runtime), `DisplayClusterMultiUser` (Runtime), `DisplayClusterOperator` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterRemoteControlInterceptor` (Runtime), `DisplayClusterReplication` (Runtime), `DisplayClusterScenePreview` (Runtime), `DisplayClusterShaders` (Runtime), `DisplayClusterStageMonitoring` (Runtime), `DisplayClusterTests` (Runtime), `DisplayClusterWarp` (Runtime), `SharedMemoryMedia` (Runtime), `SharedMemoryMediaEditor` (Runtime), `ScalableMPCDI` (External) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

nDisplay 是 UE5 的**多机同步集群渲染**系统，解决的核心问题是：**如何让多台 PC 同步渲染同一场景，并将画面分别输出到多个物理显示器或投影仪上，组成一个无缝的大画面**。

具体来说，nDisplay 负责：

1. **多机同步**：通过网络协议让多台机器的渲染帧严格同步，保证每台机器在同一时刻渲染同一帧
2. **视锥分割**：将一个大画面的视锥（Frustum）按物理屏幕/投影仪位置分割到各个渲染节点
3. **投影校正（Warping & Blending）**：支持 MPCDI 格式的几何畸变校正（warp）和边缘融合（alpha/beta blend），确保投影仪阵列的画面对齐和亮度均匀
4. **立体渲染**：支持单目（mono）和立体（stereo）两种渲染模式
5. **ICVFX / 虚拟制片**：配合 LED 摩托墙等虚拟制片场景，提供虚拟相机、色彩校正等功能

**为什么存在？** 传统的单机渲染无法满足大型沉浸式环境（如 CAVE、LED 墙、穹幕）的需求。nDisplay 让 UE5 能够以分布式集群的方式驱动这些系统，同时内置了行业标准的投影校正格式（MPCDI）支持。

## 使用场景

- 你在搭建 **CAVE 沉浸式环境**（多面投影房间）→ 用 nDisplay 配置每面墙的投影节点和视锥
- 你在做 **LED 虚拟制片（ICVFX）**，需要摩托墙多节点同步渲染 → 用 nDisplay
- 你需要 **穹幕/环幕投影**，多台投影仪拼接成一个大画面 → 用 nDisplay + MPCDI 校正数据
- 你在搭建 **大型 LED 显示墙**，需要多台 PC 分区渲染 → 用 nDisplay
- 你需要通过 **MPCDI 标准格式** 导入第三方校准软件生成的畸变/融合数据 → 用 nDisplay 的 ScalableMPCDI 模块

## 蓝图用法

> ⚠️ **ScalableMPCDI 模块无蓝图接口。** 它是一个纯 C++ 第三方库，通过 nDisplay 的其他模块间接在编辑器和运行时中使用。

nDisplay 的主要配置通过 **编辑器 UI**（DisplayClusterConfigurator）和 **配置文件（.ndisplay）** 完成，不依赖蓝图节点。

## C++ 用法 — ScalableMPCDI 第三方库

> **注意**：以下文档专门针对 nDisplay 中集成的 **ScalableMPCDI** 外部模块。该模块是 Scalable Display Technologies 提供的 MPCDI（Multi-Projector Calibration Data Interchange）标准实现，以 BSD 许可证分发。

### 什么是 MPCDI？

MPCDI 是一种行业标准格式，用于存储和交换**多投影仪校准数据**，包括：
- **几何畸变校正（Warp）**：PFM 格式的 3D 坐标网格，将每个像素映射到正确的位置
- **Alpha 融合图（Alpha Map）**：控制投影仪边缘的亮度衰减，实现无缝拼接
- **Beta 融合图（Beta Map）**：可选的第二层融合数据
- **畸变图（Distortion Map）**：可选的额外畸变数据（Shader Lamp 专用）

MPCDI 文件本质上是一个 ZIP 包，内含 XML 描述文件 + PFM/PNG 等数据文件。

### 数据模型层次

```
Profile (根节点)
├── Display
│   └── Buffer (显示缓冲区)
│       └── Region (输出区域)
│           ├── Frustum (视锥参数，3D/a3d/sl)
│           ├── CoordinateFrame (坐标框架，sl)
│           └── FileSet (数据文件集合)
│               ├── GeometryWarpFile (几何畸变校正 PFM)
│               ├── AlphaMap (Alpha 融合图)
│               ├── BetaMap (Beta 融合图，可选)
│               └── DistortionMap (畸变图，可选)
```

### Profile 类型

| 类型 | 说明 | 需要 Frustum | 需要 CoordinateFrame |
|---|---|---|---|
| `2d` | 2D 媒体播放 | ❌ | ❌ |
| `3d` | 3D 模拟渲染 | ✅ | ❌ |
| `a3` | 高级 3D 媒体 | ❌ | ❌ |
| `sl` | Shader Lamp（投影映射） | ✅ | ✅ |

### 读取 MPCDI 文件

```cpp
#include "mpcdiReader.h"
#include "mpcdiProfile.h"

// 创建 Reader
mpcdi::Reader* Reader = mpcdi::Reader::CreateReader();

// 可选：设置是否在读取后验证
Reader->SetDoProfileValidation(true);
Reader->SetCheckVersionSupported(true);

// 从文件读取
mpcdi::Profile* Profile = nullptr;
mpcdi::MPCDI_Error Err = Reader->Read("path/to/calibration.mpcdi", Profile);

if (MPCDI_SUCCEEDED(Err))
{
    // 访问 Display -> Buffer -> Region -> FileSet
    mpcdi::Display* Display = Profile->GetDisplay();
    
    // 遍历所有 Buffer
    for (auto It = Display->GetBufferBegin(); It != Display->GetBufferEnd(); ++It)
    {
        mpcdi::Buffer* Buffer = It->second;
        
        // 遍历 Buffer 中的 Region
        for (auto RIt = Buffer->GetRegionBegin(); RIt != Buffer->GetRegionEnd(); ++RIt)
        {
            mpcdi::Region* Region = RIt->second;
            
            // 获取几何畸变数据
            mpcdi::GeometryWarpFile* WarpFile = Region->GetFileSet()->GetGeometryWarpFile();
            if (WarpFile)
            {
                int SizeX = WarpFile->GetSizeX();
                int SizeY = WarpFile->GetSizeY();
                // 通过 operator()(x,y) 访问每个像素的 3D 坐标
                mpcdi::NODE& Node = (*WarpFile)(0, 0);
                // Node.r, Node.g, Node.b 即为 3D 坐标
            }
            
            // 获取 Alpha 融合数据
            mpcdi::AlphaMap* Alpha = Region->GetFileSet()->GetAlphaMap();
            if (Alpha)
            {
                unsigned char& Val = (*Alpha)(0, 0, 0); // (x, y, channel)
                double Gamma = Alpha->GetGammaEmbedded();
            }
        }
    }
}

delete Reader;
delete Profile; // 注意：Reader 默认不拥有 Profile，需要手动释放
```

### 写入 MPCDI 文件

```cpp
#include "mpcdiCreate2DMediaProfile.h"
#include "mpcdiWriter.h"

// 创建 2D Media Profile
mpcdi::Create2DMediaProfile Creator;

// 创建 Buffer 和 Region
Creator.CreateNewBuffer("buffer1");
Creator.CreateNewRegion("buffer1", "region1");

// 获取 Region 并配置数据
mpcdi::Buffer* Buffer = Creator.GetBuffer("buffer1");
mpcdi::Region* Region = Creator.GetRegion(Buffer, "region1");

// 设置分辨率和区域位置
Region->SetResolution(1920, 1080);
Region->SetXY(0.0f, 0.0f);
Region->SetSize(1.0f, 1.0f);

// 创建几何畸变文件
Creator.CreateGeometryWarpFile(Region, 1920, 1080);

// 创建 Alpha 融合图
Creator.CreateAlphaMap(Region, 1920, 1080, mpcdi::CD_FOUR, mpcdi::BD_EIGHT);
Creator.SetGammaEmbedded(Region, 2.2);

// 验证
mpcdi::MPCDI_Error Err = Creator.ValidateProfile();

// 写入文件
mpcdi::Writer* Writer = mpcdi::Writer::CreateWriter();
Writer->SetOverwriteExistingFile(true);
Writer->SetDoProfileValidation(true);

mpcdi::Profile* Profile = Creator.GetProfile();
Err = Writer->Write("output.mpcdi", *Profile);

delete Writer;
// 如果设置了 SetDeleteProfile(true)，Creator 析构时会释放 Profile
```

### 3D 模拟 Profile

```cpp
#include "mpcdiCreate3DSimulationProfile.h"

mpcdi::Create3DSimulationProfile Creator;
Creator.CreateNewBuffer("main");
Creator.CreateNewRegion("main", "leftEye");

mpcdi::Region* Region = Creator.GetRegion("main", "leftEye");

// 3D Profile 需要设置视锥
Creator.CreateFrustum(Region);
mpcdi::Frustum* Frustum = Creator.GetFrustum(Region);
Frustum->SetYaw(0.0);
Frustum->SetPitch(0.0);
Frustum->SetRoll(0.0);
Frustum->SetLeftAngle(-45.0);
Frustum->SetRightAngle(45.0);
Frustum->SetUpAngle(30.0);
Frustum->SetDownAngle(-30.0);

// 创建畸变校正数据
Creator.CreateGeometryWarpFile(Region, 512, 512);
Creator.CreateAlphaMap(Region, 512, 512, mpcdi::CD_FOUR, mpcdi::BD_EIGHT);
```

### Shader Lamp Profile

```cpp
#include "mpcdiCreateShaderLampProfile.h"

mpcdi::CreateShaderLampProfile Creator;
Creator.CreateNewBuffer("projector");
Creator.CreateNewRegion("projector", "surface1");

mpcdi::Region* Region = Creator.GetRegion("projector", "surface1");

// Shader Lamp 需要 Frustum + CoordinateFrame + DistortionMap
Creator.CreateFrustum(Region);
Creator.CreateCoordinateFrame(Region);

mpcdi::CoordinateFrame* CF = Region->GetCoordinateFrame();
CF->SetPos(0.0, 2.5, 3.0);  // 投影仪位置
CF->SetYaw(0.0, 0.0, 0.0);
CF->SetPitch(0.0, 0.0, 0.0);
CF->SetRoll(0.0, 0.0, 0.0);

// 几何单位和 3D 数据原点
Creator.CreateGeometryWarpFile(Region, 1024, 768);
mpcdi::GeometryWarpFile* GWF = Region->GetFileSet()->GetGeometryWarpFile();
Creator.SetGeometricUnit(GWF, mpcdi::GeometricUnit_m);
Creator.SetOriginOf3DData(GWF, mpcdi::OriginOf3DData_idealEyePoint);

// 创建畸变图
Creator.CreateDistortionMap(Region, 1024, 768);
```

## Demo 示例

以下演示如何以编程方式构建一个完整的 MPCDI Profile 并写入文件，然后读回来验证。

### MPCDIReadWriteDemo.h

```cpp
#pragma once

#include "CoreMinimal.h"

class FMPCDIReadWriteDemo
{
public:
    /** 运行完整的 MPCDI 写入和读取演示 */
    static void RunDemo(const FString& OutputPath);
    
private:
    /** 写入 MPCDI 文件 */
    static bool WriteMPCDI(const FString& FilePath);
    
    /** 读取 MPCDI 文件 */
    static bool ReadMPCDI(const FString& FilePath);
};
```

### MPCDIReadWriteDemo.cpp

```cpp
#include "MPCDIReadWriteDemo.h"

// ScalableMPCDI 头文件
#include "mpcdiCreate3DSimulationProfile.h"
#include "mpcdiReader.h"
#include "mpcdiWriter.h"
#include "mpcdiProfile.h"
#include "mpcdiGeometryWarpFile.h"
#include "mpcdiAlphaMap.h"
#include "mpcdiErrors.h"

void FMPCDIReadWriteDemo::RunDemo(const FString& OutputPath)
{
    FString FilePath = FPaths::Combine(OutputPath, TEXT("demo_calibration.mpcdi"));
    
    UE_LOG(LogTemp, Log, TEXT("MPCDI Demo: Writing to %s"), *FilePath);
    if (WriteMPCDI(FilePath))
    {
        UE_LOG(LogTemp, Log, TEXT("MPCDI Demo: Write succeeded. Now reading back..."));
        ReadMPCDI(FilePath);
    }
}

bool FMPCDIReadWriteDemo::WriteMPCDI(const FString& FilePath)
{
    // 1. 创建 3D Simulation Profile
    mpcdi::Create3DSimulationProfile Creator;
    
    // 设置级别（1-4，会根据添加的数据自动提升）
    Creator.SetLevel(1);
    
    // 2. 创建 Display -> Buffer -> Region 层次结构
    Creator.CreateNewBuffer("mainBuffer");
    Creator.CreateNewRegion("mainBuffer", "centerRegion");
    
    mpcdi::Buffer* Buffer = Creator.GetBuffer("mainBuffer");
    mpcdi::Region* Region = Creator.GetRegion(Buffer, "centerRegion");
    
    if (!Region)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create region"));
        return false;
    }
    
    // 3. 设置区域属性
    Region->SetResolution(64, 64);
    Region->SetXY(0.0f, 0.0f);
    Region->SetSize(1.0f, 1.0f);
    
    // 4. 创建 3D 视锥
    Creator.CreateFrustum(Region);
    mpcdi::Frustum* Frustum = Creator.GetFrustum(Region);
    Frustum->SetYaw(0.0);
    Frustum->SetPitch(0.0);
    Frustum->SetRoll(0.0);
    Frustum->SetLeftAngle(-30.0);
    Frustum->SetRightAngle(30.0);
    Frustum->SetUpAngle(20.0);
    Frustum->SetDownAngle(-20.0);
    
    // 5. 创建几何畸变文件（PFM 数据）
    const int WarpRes = 64;
    Creator.CreateGeometryWarpFile(Region, WarpRes, WarpRes);
    mpcdi::GeometryWarpFile* WarpFile = Region->GetFileSet()->GetGeometryWarpFile();
    
    if (WarpFile)
    {
        // 填充简单的网格数据（实际使用时由校准软件生成）
        for (int Y = 0; Y < WarpRes; ++Y)
        {
            for (int X = 0; X < WarpRes; ++X)
            {
                mpcdi::NODE& Node = (*WarpFile)(X, Y);
                Node.r = static_cast<float>(X) / WarpRes;
                Node.g = static_cast<float>(Y) / WarpRes;
                Node.b = 0.0f;
            }
        }
    }
    
    // 6. 创建 Alpha 融合图
    const int AlphaRes = 64;
    Creator.CreateAlphaMap(Region, AlphaRes, AlphaRes, mpcdi::CD_FOUR, mpcdi::BD_EIGHT);
    Creator.SetGammaEmbedded(Region, 2.2);
    
    mpcdi::AlphaMap* Alpha = Region->GetFileSet()->GetAlphaMap();
    if (Alpha)
    {
        // 填充全白不透明的 Alpha（无边缘融合）
        for (int Y = 0; Y < AlphaRes; ++Y)
        {
            for (int X = 0; X < AlphaRes; ++X)
            {
                for (int C = 0; C < 4; ++C)
                {
                    (*Alpha)(X, Y, C) = 255;
                }
            }
        }
    }
    
    // 7. 验证 Profile
    mpcdi::MPCDI_Error Err = Creator.ValidateProfile();
    if (MPCDI_FAILED(Err))
    {
        UE_LOG(LogTemp, Error, TEXT("Profile validation failed: %d"), (int)Err);
        UE_LOG(LogTemp, Error, TEXT("Error detail: %s"), 
               *FString(mpcdi::ErrorHelper::GetLastError().c_str()));
        return false;
    }
    
    // 8. 写入文件
    mpcdi::Writer* Writer = mpcdi::Writer::CreateWriter();
    Writer->SetOverwriteExistingFile(true);
    Writer->SetDoProfileValidation(true);
    
    mpcdi::Profile* Profile = Creator.GetProfile();
    Err = Writer->Write(TCHAR_TO_UTF8(*FilePath), *Profile);
    
    bool bSuccess = MPCDI_SUCCEEDED(Err);
    if (!bSuccess)
    {
        UE_LOG(LogTemp, Error, TEXT("Write failed: %d"), (int)Err);
        UE_LOG(LogTemp, Error, TEXT("Error detail: %s"), 
               *FString(mpcdi::ErrorHelper::GetLastError().c_str()));
    }
    
    delete Writer;
    return bSuccess;
}

bool FMPCDIReadWriteDemo::ReadMPCDI(const FString& FilePath)
{
    // 1. 创建 Reader
    mpcdi::Reader* Reader = mpcdi::Reader::CreateReader();
    Reader->SetDoProfileValidation(true);
    Reader->SetCheckVersionSupported(true);
    
    // 2. 读取文件
    mpcdi::Profile* Profile = nullptr;
    mpcdi::MPCDI_Error Err = Reader->Read(TCHAR_TO_UTF8(*FilePath), Profile);
    
    if (MPCDI_FAILED(Err))
    {
        UE_LOG(LogTemp, Error, TEXT("Read failed: %d"), (int)Err);
        delete Reader;
        return false;
    }
    
    // 3. 输出 Profile 信息
    UE_LOG(LogTemp, Log, TEXT("Profile Level: %d"), Profile->GetLevel());
    UE_LOG(LogTemp, Log, TEXT("Profile Date: %s"), 
           *FString(Profile->GetDate().c_str()));
    
    // 4. 遍历数据结构
    mpcdi::Display* Display = Profile->GetDisplay();
    for (auto BufIt = Display->GetBufferBegin(); BufIt != Display->GetBufferEnd(); ++BufIt)
    {
        mpcdi::Buffer* Buffer = BufIt->second;
        UE_LOG(LogTemp, Log, TEXT("Buffer: %s"), 
               *FString(Buffer->GetId().c_str()));
        
        for (auto RegIt = Buffer->GetRegionBegin(); RegIt != Buffer->GetRegionEnd(); ++RegIt)
        {
            mpcdi::Region* Region = RegIt->second;
            UE_LOG(LogTemp, Log, TEXT("  Region: %s (%dx%d)"),
                   *FString(Region->GetId().c_str()),
                   Region->GetXresolution(), Region->GetYresolution());
            
            mpcdi::FileSet* FS = Region->GetFileSet();
            
            // 读取几何畸变数据
            mpcdi::GeometryWarpFile* Warp = FS->GetGeometryWarpFile();
            if (Warp)
            {
                UE_LOG(LogTemp, Log, TEXT("    Warp: %dx%d"), 
                       Warp->GetSizeX(), Warp->GetSizeY());
            }
            
            // 读取 Alpha 数据
            mpcdi::AlphaMap* Alpha = FS->GetAlphaMap();
            if (Alpha)
            {
                UE_LOG(LogTemp, Log, TEXT("    Alpha: %dx%d, Gamma=%.1f"),
                       Alpha->GetSizeX(), Alpha->GetSizeY(),
                       Alpha->GetGammaEmbedded());
            }
        }
    }
    
    delete Reader;
    delete Profile;
    return true;
}
```

## 模块依赖

以下列出 ScalableMPCDI 模块的**特殊依赖**。nDisplay 整体的模块依赖非常庞大（29 个模块），此处聚焦 ScalableMPCDI。

| 模块 | 用途 |
|---|---|
| `D3D12RHI` | Direct3D 12 渲染硬件接口（通过 DisplayClusterMedia 等模块间接依赖） |

> **ScalableMPCDI 自身**：作为纯 C++ 外部库，仅依赖标准 C++ 库和内嵌的第三方库（tinyxml2、zlib/zip），无 UE 模块依赖。

> **nDisplay 整体**的模块依赖较复杂，关键的独特依赖包括：
> - `DisplayClusterProjection`：投影映射和 MPCDI 数据处理
> - `DisplayClusterMedia`：媒体输入输出（依赖 D3D12RHI）
> - `SharedMemoryMedia`：共享内存通信（依赖 D3D12RHI）
> - `DisplayClusterRemoteControlInterceptor`：远程控制接口
> - `DisplayClusterMultiUser`：多用户协作

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | 为 nDisplay 的 MovieGraph 添加 EXR 多层输出支持 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | MoviePipeline 中将 WarpBlendAlpha 模式合并进 WarpBlend |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复拓扑感知相机命名和 MPCDI/ICVFX 着色器中的不透明 Alpha 问题 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 输出帧编码回退时正确处理非默认 DisplayGamma |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复 GUI 纹理尺寸小于视口尺寸时的闪烁问题 |

### 维护评价

**⚠️ nDisplay 是 UE5 中维护最活跃的大型插件之一。**

- **创建时间**：2018 年（UE 4.20 时代），已发展 8 年
- **更新频率**：最近一周内有 5 次提交，更新极为活跃
- **功能演进**：持续添加新功能（EXR 多层、MovieGraph 集成、ICVFX 改进）
- **Bug 修复**：定期修复渲染问题、着色器问题
- **模块规模**：29 个子模块，1351 个源文件，属于超大型插件
- **启用方式**：`EnabledByDefault=false`，需要在项目设置中手动启用
- **平台支持**：Win64 + Linux

**ScalableMPCDI 模块特别说明**：这是一个嵌入的第三方库（Scalable Display Technologies, BSD 许可证），代码基础可追溯到 2012 年。该库本身是稳定的 MPCDI 标准实现，nDisplay 团队会根据需要对其进行适配和更新（如近期的 MPCDI 着色器修复）。

**推荐使用**：如果你的项目涉及多投影仪、LED 墙、虚拟制片或任何需要集群渲染的场景，nDisplay 是 UE5 的**官方且唯一**的解决方案，强烈推荐使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- [ScalableMPCDI 源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay/Source/ThirdParty/ScalableMPCDI)
- 官方文档（.uplugin 中 DocsURL 为空，请参考 UE 官方文档站的 nDisplay 章节）