import wpilib, wpimath
from wpilib.interfaces import GenericHID
from wpimath.geometry import Pose2d, Rotation2d, Translation2d


from wpimath.trajectory import TrajectoryConfig, Trajectory, TrajectoryUtil, TrajectoryGenerator, TrajectoryParameterizer
from wpimath.controller import ProfiledPIDController, PIDController

from commands2 import Swerve4ControllerCommand

import ntcore, rev, ctre, commands2
import commands2.button

import constants
from constants import AutoConstants

from commands.TeleopCommands.SwerveJoystickCmd import SwerveJoystickCmd

from wpilib import Joystick

from subsystems.armsubsystem import ArmSubsystem 
from subsystems.swervesubsystem import SwerveSubsystem
import math
import photonvision

class RobotContainer:
    """
    This class is where the bulk of the robot should be declared. Since Command-based is a
    "declarative" paradigm, very little robot logic should actually be handled in the :class:`.Robot`
    periodic methods (other than the scheduler calls). Instead, the structure of the robot (including
    subsystems, commands, and button mappings) should be declared here.
    """

    def __init__(self) -> None:
        
        self.driverController = wpilib.XboxController(constants.kDriverControllerPort) # can also use ps4 controller (^v^)
        self.operatorController = wpilib.XboxController(constants.kArmControllerPort)

        #Arm motor controllers
        # self.grabbingArm = rev.CANSparkMax(constants.grabbingArmID, rev.CANSparkMaxLowLevel.MotorType.kBrushed) #type: rev._rev.CANSparkMaxLowLevel.MotorType
        # self.extendingArm = rev.CANSparkMax(constants.extendingArmID, rev.CANSparkMaxLowLevel.MotorType.kBrushless)
        # self.rotatingArm = rev.CANSparkMax(constants.rotatingArmID, rev.CANSparkMaxLowLevel.MotorType.kBrushless)

        #Arm motor encoders
        # self.grabbingArmEncoder = wpilib.Counter(wpilib._wpilib.DigitalInput(constants.grabbingArmEncoderPort))
        # self.extendingArmEncoder = self.extendingArm.getEncoder()
        # self.rotatingArmEncoder = self.rotatingArm.getEncoder()

        #^ forward is grabbing, we may need to switch this
        # self.grabbingArmOpenLimitSwitch = self.grabbingArm.getReverseLimitSwitch(rev.SparkMaxLimitSwitch.Type.kNormallyOpen)
        # self.grabbingArmClosedLimitSwitch = self.grabbingArm.getForwardLimitSwitch(rev.SparkMaxLimitSwitch.Type.kNormallyOpen)
        # self.extendingArmMaxLimitSwitch = self.extendingArm.getReverseLimitSwitch(rev.SparkMaxLimitSwitch.Type.kNormallyOpen)
        # self.extendingArmMinLimitSwitch = self.extendingArm.getForwardLimitSwitch(rev.SparkMaxLimitSwitch.Type.kNormallyOpen)
        # self.rotatingArmMaxLimitSwitch = self.rotatingArm.getReverseLimitSwitch(rev.SparkMaxLimitSwitch.Type.kNormallyOpen)
        # self.rotatingArmMinLimitSwitch = self.rotatingArm.getForwardLimitSwitch(rev.SparkMaxLimitSwitch.Type.kNormallyOpen)

        # The robot's subsystems
        self.Swerve = SwerveSubsystem()

        self.Swerve.setDefaultCommand(SwerveJoystickCmd(
                self.Swerve,
                self.driverController.getLeftY(),
                self.driverController.getLeftX(),
                self.driverController.getRightX(),
                not self.driverController.getLeftBumperPressed()
            ))
    #     self.configureButtonBindings()

    # def configureButtonBindings(self):
    #     Joystick.button(self.driver_joystick, 2).whenPressed(lambda: self.swerve.zeroHeading())

        
        self.chooser = wpilib.SendableChooser()

        # self.chooser.setDefaultOption("cubeAuto", self.cubeToBalance )
        # self.chooser.addOption("simple auto", self.simpleAuto)

        # # Put the chooser on the dashboard
        # self.shuffle = wpilib.SmartDashboard
        # self.shuffle.putData("Autonomousff", self.chooser)
        # self.shuffle.putData("moveTest", self.moveTest)
        # self.shuffle.putData("dropOffAngle", self.dropOffAngle)
        # self.shuffle.putData("dropOffExtend", self.dropOffExtend)
        # self.shuffle.putData("dropObject", self.dropObject)

        self.camera = photonvision.PhotonCamera("Microsoft_LifeCam_HD-3000")
    def getAutonomousCommand(self) -> commands2.Command:
        """Returns the autonomous command to run"""

        # 1. Create Trajectory settings
        self.trajectoryConfig = TrajectoryConfig(
            AutoConstants.kMaxSpeedMetersPerSecond,
            AutoConstants.kMaxAccelerationMetersPerSecondSquared).setKinematics(
            constants.kDriveKinematics)

        # 2. Generate Trajectory
        self.trajectory = TrajectoryGenerator.generateTrajectory(
            # ? initial location and rotation
            Pose2d(0, 0, Rotation2d(0)),
            [
                # ? points we want to hit
                Translation2d(1, 0),
                Translation2d(1, 1),
                Translation2d(0, 1),
            ],
            # ? final location and rotation
            Pose2d(0, 0, Rotation2d(180)),
            self.trajectoryConfig
        )

        # 3. Create PIdControllers to correct and track trajectory
        self.xController = PIDController(AutoConstants.kPXController, 0, 0)
        self.yController = PIDController(AutoConstants.kPYController, 0, 0)
        self.thetaController = ProfiledPIDController(
            AutoConstants.kPThetaController, 0, 0, AutoConstants.kThetaControllerConstraints)
        self.thetaController.enableContinuousInput(-math.pi, math.pi)

        # 4. Construct command to follow trajectory
        self.swerveControllerCommand = Swerve4ControllerCommand(
            self.trajectory,
            self.Swerve.getPose,
            constants.kDriveKinematics,
            self.xController,
            self.yController,
            self.thetaController,
            self.Swerve.getModuleStates,
            self.Swerve
        )

        # 5. Add some init and wrap up, and return command 
        self.square = commands2.SequentialCommandGroup(
            commands2.InstantCommand(self.Swerve.resetOdometry(self.trajectory.getInitialPose())),
            self.swerveControllerCommand,
            commands2.InstantCommand(self.swerve.stopModules())
        )


        return self.square

        #optimize clip https://youtu.be/0Xi9yb1IMyA?t=225