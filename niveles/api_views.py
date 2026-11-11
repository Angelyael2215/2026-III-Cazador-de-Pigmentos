from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .authentication import FirebaseAuthentication
from .models import Level, LevelProgress, Player
from .services import submit_level_answer


def get_player(uid):
    player, _ = Player.objects.get_or_create(firebase_uid=uid)
    return player


def public_level(level):
    return {
        "number": level.number,
        "kind": level.kind,
        "title": level.title,
        "instruction": level.instruction,
        "data": level.data,
    }


class LevelListView(APIView):
    authentication_classes = [FirebaseAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        player = get_player(request.user.uid)
        progress = {
            item.level.number: item
            for item in LevelProgress.objects.filter(player=player).select_related("level")
        }

        levels = []
        for level in Level.objects.filter(active=True).order_by("number"):
            item = progress.get(level.number)
            levels.append({
                **public_level(level),
                "unlocked": level.number <= player.current_level_reached,
                "completed": item.completed if item else False,
            })

        return Response({
            "current_level_reached": player.current_level_reached,
            "levels": levels,
        })


class AnswerSerializer(serializers.Serializer):
    answer = serializers.DictField()


class SubmitAnswerView(APIView):
    authentication_classes = [FirebaseAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, number):
        serializer = AnswerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        level = get_object_or_404(Level, number=number, active=True)

        with transaction.atomic():
            player = get_player(request.user.uid)
            player = Player.objects.select_for_update().get(pk=player.pk)

            if number > player.current_level_reached:
                raise PermissionDenied("Primero completa los niveles anteriores.")

            try:
                progress, correct, earned_xp, earned_pigments = submit_level_answer(
                    player,
                    level,
                    serializer.validated_data["answer"],
                )
            except (KeyError, ValueError) as error:
                raise serializers.ValidationError({"answer": str(error)}) from error

        return Response({
            "correct": correct,
            "completed": progress.completed,
            "attempts": progress.attempts,
            "earned_xp": earned_xp,
            "earned_pigments": earned_pigments,
            "current_level_reached": player.current_level_reached,
        })
